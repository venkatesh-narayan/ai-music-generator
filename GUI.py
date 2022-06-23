# this file contains the code to create the overall GUI, and is the main 
# file of this entire project; every feature i've created is used in this file

from synthesize_effects import *
from generate_story import *
from generate_background_music import *
from scrape_midis import *
from GUI_elements import *

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
from pydub import AudioSegment
import pyaudio
import wave

import os
import pygame.mixer as mixer
       
class GoodGUI:
    def __init__(self):
        # create window and make it the size of the screen
        self.root = tk.Tk()
        self.root.title('Become Your Artist')
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f'{self.width}x{self.height}')

        mixer.init()
        self.prev_name = ''

    # make the first panel (the panel you see on startup of the app)
    def startup(self):
        # add spacing and make the background deep sky blue
        self.root['padx'] = 10
        self.root['pady'] = 10
        self.root.configure(bg='deep sky blue')
        
        # create a frame which has info about Become Your Artist
        self.intro_frame = NiceFrame(self.root, self.width - 20, self.height/3, 2, 'SeaGreen1',
                                     'About Become Your Artist', 'black', 'deep sky blue')
        intro_label1 = tk.Label(self.intro_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Do you want to be like your favorite artist?')
        intro_label2 = tk.Label(self.intro_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Do you need help generating background music?')
        intro_label3 = tk.Label(self.intro_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='What about content for lyrics?')
        intro_label4 = tk.Label(self.intro_frame, font=('marker felt', 30),
                                fg='black', bg='deep sky blue',
                                text='Become Your Artist')
        intro_label5 = tk.Label(self.intro_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='is your solution!')

        # place on screen
        self.intro_frame.place(relx=0, rely=0)
        intro_label1.place(relx=0.5, rely=0.2, anchor='center')
        intro_label2.place(relx=0.5, rely=0.4, anchor='center')
        intro_label3.place(relx=0.5, rely=0.6, anchor='center')
        intro_label4.place(relx=0.436, rely=0.8, anchor='center')
        intro_label5.place(relx=0.56, rely=0.8, anchor='center')

        # create a frame which has features you can use
        self.actions_frame = NiceFrame(self.root, self.width - 20, 100, 2, 'IndianRed1',
                                       'What You Can Do', 'black', 'deep sky blue')

        go_to_music = RoundButton(self.actions_frame, 250, 50, 25, 2, 'purple1', 'Create Background Music', 'black',
                                 command=self.background_music_panel)
        go_to_synthesis = RoundButton(self.actions_frame, 250, 50, 25, 2, 'purple1', 'Synthesize Voice Effects', 'black', 
                                     command=self.synthesis_panel)
        go_to_story_gen = RoundButton(self.actions_frame, 250, 50, 25, 2, 'purple1', 'Generate Lyrical Content', 'black', 
                                     command=self.story_panel)
        
        # place on screen
        self.actions_frame.place(relx=0, rely=0.5)
        go_to_music.place(relx=0.225, rely=0.5, anchor='w')
        go_to_synthesis.place(relx=0.425, rely=0.5, anchor='w')
        go_to_story_gen.place(relx=0.625, rely=0.5, anchor='w')

        image = ImageTk.PhotoImage(Image.open('/Users/venkatesh/Desktop/112 homework/term project/images/own_music.jpg'))
        self.own_music = tk.Label(self.root, image=image)
        self.own_music.place(relx=0.35, rely=0.65)

        self.root.mainloop()
    
    # creating background music panel
    def background_music_panel(self):
        # remove the old frames from the startup panel
        self.intro_frame.place_forget()
        self.actions_frame.place_forget()
        self.own_music.place_forget()

        # create a frame that tells the user how to use the feature
        self.music_frame = NiceFrame(self.root, self.width - 20, self.height/3, 2, 'SeaGreen1',
                                     'How To Make Music With Us', 'black', 'deep sky blue')
        music_label1 = tk.Label(self.music_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='You want to make some music!! Great!')
        music_label2 = tk.Label(self.music_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="We've made it super easy to do that...")
        music_label3 = tk.Label(self.music_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='All you have to do is enter the name of an artist in the text box underneath!')

        # place on screen
        self.music_frame.place(relx=0, rely=0)
        music_label1.place(relx=0.5, rely=0.2, anchor='center')
        music_label2.place(relx=0.5, rely=0.5, anchor='center')
        music_label3.place(relx=0.5, rely=0.8, anchor='center')
        
        # create a frame which allows the user to use the feature
        self.music_gen_frame = NiceFrame(self.root, self.width - 20, 200, 2, 'IndianRed1',
                                   'Generate Music!', 'black', 'deep sky blue')
        
        artist_name = tk.Label(self.music_gen_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Name of Artist: ')
        self.name_entered = tk.Entry(self.music_gen_frame)
        make_music = RoundButton(self.music_gen_frame, 150, 50, 25, 2, 'purple1', 'Make Music', 'black',
                                 command=self.make_music_command)

        self.play_music = RoundButton(self.music_gen_frame, 150, 50, 25, 2, 'purple1', 'Play Music', 'black',
                                 command=self.play_music_command)

        # create a button to go back to the startup panel
        self.back = RoundButton(self.root, 150, 50, 25, 2, 'purple1', 'Back', 'black',
                                 command=self.go_back_background)
        
        # place on screen
        self.music_gen_frame.place(relx=0, rely=0.5)
        artist_name.place(relx=0.1, rely=0.5, anchor='w')
        self.name_entered.place(relx=0.3, rely=0.5, anchor='w')
        make_music.place(relx=0.5, rely=0.5, anchor='w')
        self.play_music.place(relx=0.7, rely=0.5, anchor='w')

        self.back.place(relx=0.9, rely=0.9)

    # synthesize voice effects panel
    def synthesis_panel(self):
        # remove the frames from the startup panel
        self.intro_frame.place_forget()
        self.actions_frame.place_forget()
        self.own_music.place_forget()

        # create a frame which allows the user to record themselves
        self.record_frame = NiceFrame(self.root, self.width - 20, self.height / 4, 2, 'SeaGreen1',
                                      'Recording', 'black', 'deep sky blue')
        record_label1 = tk.Label(self.record_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Time to record yourself!')
        record_label2 = tk.Label(self.record_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="Press record to start, and play to listen!")
        
        record_button = RoundButton(self.record_frame, 150, 50, 25, 2, 'purple1', 'Record', 'black',
                                    command=self.record_command)
        
        self.play_inp_button = RoundButton(self.record_frame, 150, 50, 25, 2, 'purple1', 'Play', 'black',
                                           command=self.play_input_command)

        # place on screen
        self.record_frame.place(relx=0, rely=0)
        record_label1.place(relx=0.5, rely=0.2, anchor='center')
        record_label2.place(relx=0.5, rely=0.4, anchor='center')
        record_button.place(relx=0.4, rely=0.8, anchor='center')
        self.play_inp_button.place(relx=0.6, rely=0.8, anchor='center')

        # create a frame with effects the user can add to their recording
        self.effects_frame = NiceFrame(self.root, self.width - 20, self.height / 2 + 25, 2, 'IndianRed1',
                                      'Using Effects', 'black', 'deep sky blue')
        effects_label1 = tk.Label(self.effects_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="Great! Now that you're done, choose the effects you want to add!")
        effects_label2 = tk.Label(self.effects_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="If you don't want any, then just click the 'synthesize' button below to get the finished output!")
        
        artist_name = tk.Label(self.effects_frame, font=('marker felt', 30),
                                fg='black', bg='deep sky blue',
                                text='Name of Artist: ')
        self.name_entered = tk.Entry(self.effects_frame)

        # make buttons with all the effects
        clear_effects = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Clear Effects', 'black',
                                    command=self.clear_command)
        norm = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Normalize', 'black',
                           command=self.norm_command)
        overdrive = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Distort', 'black',
                                command=self.overdrive_command)
        phaser = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Phasing', 'black',
                             command=self.phaser_command)
        reverb = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Reverb', 'black',
                                command=self.reverb_command)
        tremolo = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Tremolo', 'black',
                             command=self.tremolo_command)

        bass = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Bass (enter dB)', 'black',
                           command=self.bass_command)
        self.b_gain_db = tk.Entry(self.effects_frame)
        speed = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Speed (enter ratio)', 'black',
                            command=self.speed_command)
        self.factor = tk.Entry(self.effects_frame)
        treble = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Treble (enter dB)', 'black',
                             command=self.treble_command)
        self.t_gain_db = tk.Entry(self.effects_frame)

        synthesize = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Synthesize', 'black',
                             command=self.synthesize_command)

        self.play_final = RoundButton(self.effects_frame, 150, 50, 25, 2, 'purple1', 'Play', 'black',
                             command=self.play_final_command)

        # button to go back to startup panel
        self.back = RoundButton(self.root, 150, 50, 25, 2, 'purple1', 'Back', 'black',
                             command=self.go_back_synthesis)
        
        # place on screen
        self.effects_frame.place(relx=0, rely=0.3)
        artist_name.place(relx=0.35, rely=0.1, anchor='w')
        self.name_entered.place(relx=0.5, rely=0.1, anchor='w')

        clear_effects.place(relx=0.35, rely=0.2)
        norm.place(relx=0.51, rely=0.2)
        overdrive.place(relx=0.66, rely=0.2)
        phaser.place(relx=0.35, rely=0.35)
        reverb.place(relx=0.51, rely=0.35)
        tremolo.place(relx=0.66, rely=0.35)
        bass.place(relx=0.35, rely=0.5)
        self.b_gain_db.place(relx=0.5, rely=0.5)
        speed.place(relx=0.35, rely=0.65)
        self.factor.place(relx=0.5, rely=0.65)
        treble.place(relx=0.35, rely=0.8)
        self.t_gain_db.place(relx=0.5, rely=0.8)
        synthesize.place(relx=0.51, rely=0.9)
        self.play_final.place(relx=0.66, rely=0.9)
        self.back.place(relx=0.9, rely=0.9)

    # generate story panel
    def story_panel(self):
        # remove frames from the startup panel
        self.intro_frame.place_forget()
        self.actions_frame.place_forget()
        self.own_music.place_forget()

        # create a frame which tells the user how to use the feature
        self.story_frame = NiceFrame(self.root, self.width - 20, 200, 2, 'SeaGreen1',
                                     'How To Generate A Story', 'black', 'deep sky blue')

        story_label1 = tk.Label(self.story_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Results may vary.')
        story_label2 = tk.Label(self.story_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="Need some help to write your content? We're here for you.")
        story_label3 = tk.Label(self.story_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text="Just enter the name of an artist whose content you want to mimic and a small starter sentence. We'll generate the rest.")
        
        # place on screen
        self.story_frame.place(relx=0, rely=0)
        story_label1.place(relx=0.5, rely=0.2, anchor='center')
        story_label2.place(relx=0.5, rely=0.5, anchor='center')
        story_label3.place(relx=0.5, rely=0.8, anchor='center')

        # create a frame which lets the user use the feature
        self.story_gen_frame = NiceFrame(self.root, self.width - 20, self.height/2, 2, 'IndianRed1',
                                         'Make A Story', 'black', 'deep sky blue')
        
        artist_name = tk.Label(self.story_gen_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Name of Artist: ')
        self.name_entered = tk.Entry(self.story_gen_frame)
        starter = tk.Label(self.story_gen_frame, font=('marker felt', 30),
                                fg='purple3', bg='deep sky blue',
                                text='Starter: ')
        self.starter_entered = tk.Entry(self.story_gen_frame)
        make_story = RoundButton(self.story_gen_frame, 250, 50, 25, 2, 'purple1', 'Generate Story', 'black',
                                 command=self.story_command)

        # button to go back to startup panel
        self.back = RoundButton(self.root, 150, 50, 25, 2, 'purple1', 'Back', 'black',
                                 command=self.go_back_story)
        
        # place on screen
        self.story_gen_frame.place(relx=0, rely=0.3)
        artist_name.place(relx=0.125, rely=0.15, anchor='w')
        self.name_entered.place(relx=0.250, rely=0.15, anchor='w')
        starter.place(relx=0.4, rely=0.15, anchor='w')
        self.starter_entered.place(relx=0.500, rely=0.15, anchor='w')
        make_story.place(relx=0.65, rely=0.15, anchor='w')

        self.back.place(relx=0.9, rely=0.9)

    # button commands below

    # makes music
    def make_music_command(self):
        # only do things if valid input is entered
        if self.name_entered.get() == '': return

        # set current value of name
        self.prev_name = self.name_entered.get()

        # create progressbar
        progress = ProgressBar(self.music_gen_frame, 150, 150, 20, 'Getting MIDIs...', 
                               'black', 0, 'deep sky blue')
        
        progress.place(relx= 0.85, rely=0.15)

        # update frame
        self.music_gen_frame.update()
        self.music_gen_frame.update_idletasks()

        # start threading
        thread_getMIDIs = threading.Thread(target=getMIDIs, 
                                           args=(self.name_entered.get(),))
        thread_getMIDIs.start()
        thread_getMIDIs.join()

        # after finished, update progress bar
        progress.place_forget()
        progress = ProgressBar(self.music_gen_frame, 150, 150, 20, 'Making music...', 
                               'black', 0.50, 'deep sky blue')
        progress.place(relx= 0.85, rely=0.15)
        self.music_gen_frame.update()
        self.music_gen_frame.update_idletasks()

        # start generating new music
        thread_generate = threading.Thread(target=generate_new_sequence,
                                            args=(self.name_entered.get(),))
        thread_generate.start()
        thread_generate.join()

        # after finished, update progress bar
        progress.place_forget()
        progress = ProgressBar(self.music_gen_frame, 150, 150, 20, 'Finished!', 
                               'black', 1, 'deep sky blue')
        progress.place(relx= 0.85, rely=0.15)
        self.music_gen_frame.update()
        self.music_gen_frame.update_idletasks()

        # "remove" the progress bar and value label
        progress.place_forget()
        self.music_gen_frame.update()
        self.music_gen_frame.update_idletasks()

        # reset current music split after having made new music
        self.current_music_split = None

    # plays music
    def play_music_command(self):
        # only do this if valid input is entered
        if self.name_entered.get() == '': return

        # use pygame mixer to play the song
        name = self.name_entered.get()
        path = '/Users/venkatesh/Desktop/112 homework/term project/background_'

        # if the name changes, reset name & times clicked
        if name != self.prev_name:
            self.prev_name = name
            self.play_music.times_clicked = 1
        
        # first time
        if self.play_music.times_clicked == 1:
            mixer.music.load(path + name.replace(' ', '_') + '.wav')
            mixer.music.play()
        
        # not first time, but clicked an odd number of times
        elif self.play_music.times_clicked % 2 == 1:
            mixer.music.unpause()
        
        # clicked an even number of times, so pause music
        else:
            mixer.music.pause()

    # play user recorded music
    def play_input_command(self):
        # only do this if it's been recorded
        if not os.path.exists('/Users/venkatesh/Desktop/112 homework/term project/input.wav'): return

        # first time
        if self.play_inp_button.times_clicked == 1:
            mixer.music.load('/Users/venkatesh/Desktop/112 homework/term project/input.wav')
            mixer.music.play()
        
        # not first time, but clicked an odd number of times
        elif self.play_inp_button.times_clicked % 2 == 1:
            mixer.music.unpause()
        
        # clicked an even number of times, so pause music
        else:
            mixer.music.pause()
    
    def play_final_command(self):
        if self.name_entered.get() == '': return

        # first time
        if self.play_final.times_clicked == 1:
            mixer.music.load('/Users/venkatesh/Desktop/112 homework/term project/final.wav')
            mixer.music.play()
        
        # not first time, but clicked an odd number of times
        elif self.play_final.times_clicked % 2 == 1:
            mixer.music.unpause()
        
        # clicked an even number of times, so pause music
        else:
            mixer.music.pause()

    # creates a story
    def story_command(self):
        # only do this if valid input is entered
        if self.name_entered.get() == '' or self.starter_entered.get() == '': return

        # thread to save all lyrics
        thread_get_lyrics = threading.Thread(target=get_all_lyrics,
                                             args=(self.name_entered.get(),))
        # start threading
        thread_get_lyrics.start()
        thread_get_lyrics.join()

        # thread to make story (using static function defined in StoryGenerator)
        res = StoryGenerator.run_thread(self.name_entered.get(), 
                                        self.starter_entered.get())

        # update panel to have story
        self.story_name = tk.Label(self.story_gen_frame, font=('marker felt', 25),
                                fg='purple3', bg='deep sky blue',
                                text='Story: ' + res,
                                wraplength=self.story_gen_frame.winfo_width() - 200)
        
        # place on screen
        self.story_name.place(relx=0.1, rely=0.2)

    # goes back from background panel to startup
    def go_back_background(self):
        # remove all frames from the current panel
        self.music_frame.place_forget()
        self.music_gen_frame.place_forget()
        self.back.place_forget()

        # replace the frames in the startup panel
        self.intro_frame.place(relx=0, rely=0)
        self.actions_frame.place(relx=0, rely=0.5)
        self.own_music.place(relx=0.35, rely=0.65)

        # reset the times clicked when going back
        self.play_music.times_clicked = 0

        # update root to prevent lag
        self.root.update()
        self.root.update_idletasks()

    # goes back from synthesis panel to startup
    def go_back_synthesis(self):
        # remove all frames from the current panel
        self.record_frame.place_forget()
        self.effects_frame.place_forget()
        self.back.place_forget()

        # replace frames from the startup panel
        self.intro_frame.place(relx=0, rely=0)
        self.actions_frame.place(relx=0, rely=0.5)
        self.own_music.place(relx=0.35, rely=0.65)

        # update root to prevent lag
        self.root.update()
        self.root.update_idletasks()

    # goes back from story panel to startup
    def go_back_story(self):
        # remove all frames from the current panel
        self.story_frame.place_forget()
        self.story_gen_frame.place_forget()
        self.back.place_forget()

        # replace frames from the startup panel
        self.intro_frame.place(relx=0, rely=0)
        self.actions_frame.place(relx=0, rely=0.5)
        self.own_music.place(relx=0.35, rely=0.65)

        # update root to prevent lag
        self.root.update()
        self.root.update_idletasks()

    # record music
    def record_command(self):
        p = pyaudio.PyAudio()
        
        # for a mac!!
        stream = p.open(format=pyaudio.paInt16, channels=1, 
                        rate=48000, input_device_index=0, 
                        frames_per_buffer=1024, input=True)
        
        frames = []

        # 10 second recording -- will change to user defined amount later
        for i in range(int(48000 / 1024 * 11)):
            frames.append(stream.read(1024))
        
        # close everything safely
        stream.stop_stream()
        stream.close()

        p.terminate()

        # save music
        save = '/Users/venkatesh/Desktop/112 homework/term project/input.wav'
        wv = wave.open(save, 'wb')
        wv.setnchannels(1)
        wv.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wv.setframerate(48000)
        wv.writeframes(b''.join(frames))
        wv.close()
    
    # clear all effects
    def clear_command(self):
        thread_clear = threading.Thread(target=add_effects,
                                        kwargs={'clear_effects': True})
        thread_clear.start()
        thread_clear.join()
    
    # apply bass
    def bass_command(self):
        # only do this if valid input is entered
        if self.b_gain_db.get() == '': return

        thread_bass = threading.Thread(target=add_effects,
                  kwargs={'bass': True, 'b_gain_db': int(self.b_gain_db.get())})
        thread_bass.start()
        thread_bass.join()
    
    # apply normalizing effect
    def norm_command(self):
        thread_norm = threading.Thread(target=add_effects,
                                       kwargs={'norm': True})
        thread_norm.start()
        thread_norm.join()
    
    # apply distortion
    def overdrive_command(self):
        thread_overdrive = threading.Thread(target=add_effects,
                                            kwargs={'overdrive': True})
        thread_overdrive.start()
        thread_overdrive.join()
    
    # apply phasing effect
    def phaser_command(self):
        thread_phaser = threading.Thread(target=add_effects,
                                         kwargs={'phaser': True})
        thread_phaser.start()
        thread_phaser.join()

    # apply reverb
    def reverb_command(self):
        thread_reverb = threading.Thread(target=add_effects,
                                         kwargs={'reverb': True})
        thread_reverb.start()
        thread_reverb.join()
    
    # change speed
    def speed_command(self):
        # only do this if valid input is entered
        if self.factor.get() == '': return

        thread_speed = threading.Thread(target=add_effects,
                       kwargs={'speed': True, 'factor': int(self.factor.get())})
        thread_speed.start()
        thread_speed.join()
    
    # apply treble
    def treble_command(self):
        # only do this if valid input is entered
        if self.t_gain_db.get() == '': return

        thread_treble = threading.Thread(target=add_effects,
              kwargs={'treble': True, 't_gain_db': int(self.t_gain_db.get())})
        thread_treble.start()
        thread_treble.join()
    
    # apply tremolo
    def tremolo_command(self):
        thread_tremolo = threading.Thread(target=add_effects,
                                          kwargs={'tremolo': True})
        thread_tremolo.start()
        thread_tremolo.join()
    
    # synthesize music
    def synthesize_command(self):
        if self.name_entered.get() == '': return

        # get all files needed
        inp = '/Users/venkatesh/Desktop/112 homework/term project/input.wav'
        out = '/Users/venkatesh/Desktop/112 homework/term project/foreground.wav'
        outx = '/Users/venkatesh/Desktop/112 homework/term project/foregroundx.wav'
        if not os.path.exists(out):
            os.rename(inp, out)
        
        # thread to synthesize music
        thread_synthesize = threading.Thread(target=get_final,
                                             args=(self.name_entered.get(),))
        # start threading
        thread_synthesize.start()
        thread_synthesize.join()

        # remove old files so that we can add different effects on the input
        # to see a new output
        os.remove(out)
        os.remove(outx)


g = GoodGUI()
g.startup()