# this file contains the code to train and validate the OpenAIGPTLM Model for
# language generation, and also uses that model to generate lyrical content
# depends on scrape_lyrics to get the lyrics and training/validation data

import torch
from torch.utils.data import *
from torch.utils.data.dataloader import *
from transformers import *
from tqdm import tqdm
from tqdm import trange
import numpy as np
import os

from scrape_lyrics import *

# inspired by (& using models from) https://github.com/huggingface/transformers
class StoryGenerator(Dataset):

    ############################ start model setup ############################

    def __init__(self, name, training=True):
        # setup needed vars
        self.train_path = '/Users/venkatesh/Desktop/112 homework/term project/training/' + name + '/'
        self.file = self.train_path + name + '_train.txt' if training == True else self.train_path + name + '_val.txt'
        self.model = OpenAIGPTLMHeadModel.from_pretrained('openai-gpt')
        self.tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')
        self.name = name # artist
        self.device = torch.device('cpu') # no cuda

        self.model.to(self.device) # send gpt model to cpu

        # create tokens and convert to ids
        self.inputs = []
        f = open(self.file, encoding='utf-8', mode='r')
        data = f.read()
        ids = self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(data))

        # 200 is just a random number; can change based on needs
        for i in range(0, len(ids) - 200 + 1, 200):
            self.inputs.append(self.tokenizer.build_inputs_with_special_tokens(ids[i:i + 200]))
        
        f.close()
    
    # required for DataLoader (used below)
    def __len__(self): return len(self.inputs)

    # required for DataLoader (used below)
    def __getitem__(self, item): return torch.tensor(self.inputs[item])
    
    def get_train_dataset(self): return StoryGenerator(self.name, training=True)

    def get_val_dataset(self): return StoryGenerator(self.name, training=False)

    # what a mask does is essentially to "hide" a word from the model
    # we want to get a model to predict the word and then use those losses
    # to backpropogate & learn
    def mask(self, batch):
        self.batch = batch
        self.lm_labels = batch.clone()

        # create the special masked tokens and put it into a tensor
        masked_tokens = []
        for entry in self.lm_labels.tolist():
            masked_tokens.append(self.tokenizer.get_special_tokens_mask(entry, already_has_special_tokens=True))
        masked_tokens = torch.tensor(masked_tokens, dtype=torch.bool)

        # 0.15 is arbitrary -- can change... but it's a good default
        masked_probability = torch.full(self.lm_labels.shape, 0.15)
        masked_probability.masked_fill_(masked_tokens, value=0.0)
        
        # here, we choose the indices that we want to change the input 
        # (ie, the batch), with; we either mask a token 80% of the time
        # (hence 0.80), make some of the indices random 10% of the time
        # (hence 0.50; 0.50 * (1 - 0.80) = 0.10), and keep normal for the rest
        loss_elems = ~torch.bernoulli(masked_probability).bool()
        mask_elems = ~loss_elems & torch.bernoulli(torch.full(self.lm_labels.shape, 0.80)).bool()
        rand_elems = ~loss_elems & ~mask_elems & torch.bernoulli(torch.full(self.lm_labels.shape, 0.50)).bool()
        rand_tokens = torch.randint(len(self.tokenizer), self.lm_labels.shape, dtype=torch.long)

        self.lm_labels[loss_elems] = -100 # id for a masked token (hidden)
        self.batch[mask_elems] = 103 # special token id
        self.batch[rand_elems] = rand_tokens[rand_elems] # random

        # send newly updated batch & labels to device
        self.batch = self.batch.to(self.device)
        self.lm_labels = self.lm_labels.to(self.device)
    
    # train model on our data
    def train(self):
        # this is very computationally expensive & takes a good amount of time;
        # if the epochs have already been ran & saved, don't run again
        if os.path.exists(f'/Users/venkatesh/Desktop/112 homework/term project/saves' + self.name.replace(' ', '_')):
            return

        # load data
        dataset = self.get_train_dataset()
        loader = DataLoader(dataset,
                            sampler=RandomSampler(dataset),
                            batch_size=4)

        # setup optimizer & scheduler; * 2 because we're running 2 epochs
        # learning rate and eps were chosen after playing around and testing
        # to see what works; can change but is a good default
        self.optimizer = AdamW(self.model.parameters(), lr=5e-5, eps=1e-8)
        self.scheduler = get_linear_schedule_with_warmup(self.optimizer,
                                                         num_warmup_steps=0,
                                                         num_training_steps=len(loader) * 2)
        # get ready for gradient descent
        self.model.zero_grad()

        #random.seed(42); np.random.seed(42); torch.manual_seed(42)

        # run 2 epochs
        for _ in trange(0, 2, desc='epoch'):
            for batch in tqdm(loader, desc='iteration'):
                self.mask(batch)
                self.model.train()

                # after the mask and train, get the outputs and the loss
                # backpropogate the computed loss
                self.outputs = self.model(self.batch, labels=self.lm_labels)
                self.training_loss = self.outputs[0]
                self.training_loss.backward(torch.ones_like(self.training_loss))

                # step the optimizer and scheduler & reset the model gradients
                # for the next iteration
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                self.scheduler.step()
                self.model.zero_grad()

    # validate model on our data; very similar to train
    def validate(self):
        # load data
        dataset = self.get_val_dataset()
        loader = DataLoader(dataset,
                           sampler=SequentialSampler(dataset),
                           batch_size=4)
        
        # set the model to evaluation mode
        self.model.eval()
        self.eval_loss = 0
        steps = 0

        # run validation
        for batch in tqdm(loader, desc='validation'):
            self.mask(batch)
            
            # calculate loss
            with torch.no_grad():
                self.outputs = self.model(self.batch, labels=self.lm_labels)
                self.eval_loss += self.outputs[0].mean().item()
            
            steps += 1

        # return how good it was; lower = better
        return torch.exp(torch.tensor(self.eval_loss / steps))
    
    
    ############################# end model setup #############################

    ############################ start model usage ############################

    # nucleus sampling technique to filter the best "words" (logits)
    def filter_best_words(self, dist):
        # sort and apply softmax (http://jalammar.github.io/illustrated-gpt2/)
        sorted_dist, indices = torch.sort(dist, descending=True)
        cumulative = torch.cumsum(torch.nn.functional.softmax(sorted_dist, dim=-1), dim=-1)

        # get indices to remove & reformat that remove data
        remove = cumulative > 0.90
        remove[..., 1:] = remove[..., :-1].clone()
        remove[..., 0] = 0

        # 'remove' them by setting to -inf
        dist[remove.scatter(dim=1, index=indices, src=remove)] = float('-inf')

        return dist

    # create a sample sequence; temperature defaulted to 1.0 but can change
    def encoded_sequence(self, tokens, temperature=1.0):
        # setup the encoded tokens
        self.tokens = torch.tensor(tokens, device=self.device, dtype=torch.long).unsqueeze(0).repeat(1, 1)
        
        with torch.no_grad():
            # chose to generate 300 words; can change
            for _ in trange(300):
                # pass in input ids to the model (the tokens) through kwargs
                model_inputs = { 'input_ids': self.tokens }
                self.outputs = self.model(**model_inputs)
                
                # generate next tokens from outputs and scale by temperature
                # apply penalty for repeating words too much (5)
                next_token = self.outputs[0][:, -1, :] / temperature
                for _ in set(self.tokens[0].tolist()):
                    next_token[0, _] /= 5

                # filter words, apply softmax, then add that to tokens
                filtered = self.filter_best_words(next_token)
                next_token = torch.multinomial(torch.nn.functional.softmax(filtered, dim=-1), num_samples=1)
                self.tokens = torch.cat((self.tokens, next_token), dim=1)

    # does all the model testing training & generation
    def generate_lyrics(self, starter):
        self.state = 'training...'

        self.train()

        self.state = 'saving...'

        # create save dir
        save_dir = f'/Users/venkatesh/Desktop/112 homework/term project/saves' + self.name.replace(' ', '_')
        if not os.path.exists(save_dir): 
            os.mkdir(save_dir)

            # save the model!!! saves so much time
            self.model.save_pretrained(save_dir)
            self.tokenizer.save_pretrained(save_dir)

        # reload models & tokenizers to proceed to validation
        self.model = OpenAIGPTLMHeadModel.from_pretrained(save_dir)
        self.tokenizer = OpenAIGPTTokenizer.from_pretrained(save_dir)
        self.model.to(self.device)

        self.state = 'validating...'

        score = self.validate()
        print("SCORE: ", score) # see how good the model is

        self.state = 'generating words...'

        # encode the given starting prompt
        start_tokens = self.tokenizer.encode(starter, add_special_tokens=False)
        self.encoded_sequence(start_tokens)
        
        # decode characters & write to file
        f = open('/Users/venkatesh/Desktop/112 homework/term project/output.txt', 'w')
        f.write(starter)
        for encoded_token in self.tokens[:, len(start_tokens):].tolist():
            text = self.tokenizer.decode(encoded_token, clean_up_tokenization_spaces=True)
            f.write(text)
            f.write('\n')
        f.close()

        self.state = ''
    
    # threading function for gui incorporation
    @staticmethod
    def run_thread(name, starter):
        data = StoryGenerator(name)

        thread_generate_lyrics = threading.Thread(target=data.generate_lyrics,
                                                  args=(starter,))
        thread_generate_lyrics.start()
        thread_generate_lyrics.join()

        return open('/Users/venkatesh/Desktop/112 homework/term project/output.txt', 'r').read()