# this file contains the code to add and synthesize user-chosen effects to
# their input, and synthesize it with the background music they created

import sox
import os
from pydub import AudioSegment

# function to add effects to user input
def add_effects(clear_effects=False, bass=False, b_gain_db=0.0, norm=False, 
                overdrive=False, phaser=False, reverb=False, speed=False, 
                factor=1, treble=False, t_gain_db=0.0, tremolo=False):
    # create a sox transformer and apply effects
    tfm = sox.Transformer()
    
    if clear_effects: tfm.clear_effects()
    if bass: tfm.bass(b_gain_db)
    if norm: tfm.norm()
    if overdrive: tfm.overdrive()
    if phaser: tfm.phaser()
    if reverb: tfm.reverb()
    if speed: tfm.speed(factor)
    if treble: tfm.treble(t_gain_db)
    if tremolo: tfm.tremolo()

    # store to output file
    inp = '/Users/venkatesh/Desktop/112 homework/term project/input.wav'
    out = '/Users/venkatesh/Desktop/112 homework/term project/foreground.wav'
    outx = '/Users/venkatesh/Desktop/112 homework/term project/foregroundx.wav'
    if os.path.exists(out): 
        os.rename(out, outx)
        tfm.build(outx, out)
    else:
        tfm.build(inp, out)


# function to overlay background beat + foreground vocals
# export final output as "final.wav"
def get_final(name):
    name = name.replace(' ', '_')
    # open foreground & background files
    path = '/Users/venkatesh/Desktop/112 homework/term project/'
    background = AudioSegment.from_wav(path + 'background_' + name + '.wav')
    foreground = AudioSegment.from_wav(path + 'foreground.wav')

    # trim to len of foreground
    background = background[:len(foreground)]

    # overlay & export
    final_track = foreground.overlay(background)
    final_track.export(path + 'final.wav', format='wav')
