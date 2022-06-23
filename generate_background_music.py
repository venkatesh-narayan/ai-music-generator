# this file contains code to set up the magenta model and use it to create music
# depends on scrape_midis.py to first get the midi files
# requires downloading of 'hierdec-trio_16bar.tar' file from website:
# https://github.com/tensorflow/magenta/tree/master/magenta/models/music_vae

# a lot of this exists in magenta music_vae demos, but i've modified it
# to suit my needs

import magenta.music as mm
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
import tensorflow as tf
import random
import decimal
from midi2audio import FluidSynth

# setup configs & model
def setup():
    path = '/Users/venkatesh/Desktop/112 homework/checkpoints/'
    hpath = path + 'hierdec-trio_16bar.tar'

    # set up configs and trained models
    hierdec_config = configs.CONFIG_MAP['hierdec-trio_16bar']
    model = TrainedModel(hierdec_config, batch_size=4, 
                         checkpoint_dir_or_path=hpath)
    
    return hierdec_config, model

# function to interpolate two sequences with each other
# relies mostly upon interpolation function in model, but it's easier to write
# one function to interpolate & concatenate the sequences
def interpolate(model, start, end, num_steps=8, length=256, 
                assert_same_length=True, temperature=0.5, duration=32):
    
    notes = model.interpolate(start, end, num_steps=num_steps, length=length,
                              temperature=temperature, 
                              assert_same_length=assert_same_length)
    
    # num_steps called in the backend will always be > 3
    return mm.sequences_lib.concatenate_sequences(notes, [duration] * len(notes))

# function to generate new sequence given the name of the artist
def generate_new_sequence(name):
    # setup configs & trained models
    hierdec_config, model = setup()

    path = '/Users/venkatesh/Desktop/112 homework/term project/' + name + '/'

    # get all midi input files for the artist
    files = [f for f in sorted(tf.io.gfile.glob(path + '*.mid'))]
    inp_files = [tf.io.gfile.GFile(f, mode='rb').read() for f in files]

    # transform midi files to note sequences
    sequences = [mm.midi_to_sequence_proto(f) for f in inp_files]
    extracted = [] # will hold all extracted melodies of songs

    representation = {}
    curr_key = 0; counter = 0
    # melody extraction -- held in tensors
    for ns in sequences:
        prev_len = len(extracted)
        extracted.extend(hierdec_config.data_converter.to_notesequences(
                         hierdec_config.data_converter.to_tensors(ns)[1]))
        curr_len = len(extracted)

        for i in range(curr_key, curr_key + curr_len - prev_len):
            representation[i] = files[counter].split('/')[-1][:-4]
        
        curr_key += curr_len - prev_len
        counter += 1

    # choosing one random index and using that as start
    # end will be the one right after it
    rand_index = random.randint(0, len(extracted) - 2)
    start = extracted[rand_index]; end = extracted[rand_index + 1]

    # choose a random temperature from 0.5 to 1.5
    temp = float(decimal.Decimal(random.randrange(5, 15)) / 10)

    print(rand_index, temp)

    print('this song will be similar to ' + representation[rand_index])

    # interpolate sequences, plot, and play
    new_seq = interpolate(model, start, end, temperature=temp)

    mm.midi_io.note_sequence_to_midi_file(new_seq, 'background_' + name.replace(' ', '_') + '.mid')

    # convert to wav
    fs = FluidSynth()
    fs.midi_to_audio('background_' + name.replace(' ', '_') + '.mid', 
                     'background_' + name.replace(' ', '_') + '.wav')
