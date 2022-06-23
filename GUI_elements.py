# this file contains code for creating my own GUI objects
# includes: circular progress bar, rounded button, labeled frame (with colors)

import tkinter as tk
from tkinter import ttk

# circular progress bar
class ProgressBar(tk.Canvas):
    def __init__(self, parent, width, height, padding, label, textcolor, percent_done, bg):
        tk.Canvas.__init__(self, parent, borderwidth=0, bg=bg, relief='flat',
                           highlightthickness=0, width=width, height=height)
        self.padding = padding
        self.width = width
        self.height = height
        self.label = label
        self.percent_done = percent_done
        self.textcolor = textcolor

        self.draw()
        dims = self.bbox('all')

        self.configure(width=dims[2] - dims[0], height=dims[3] - dims[1])
    
    # draw the circular progress bar
    def draw(self):
        # outer circle
        self.create_oval(0, 0,
                         self.width, self.height)
        
        # inner circle
        self.create_oval(self.padding, self.padding,
                         self.width - self.padding, self.height - self.padding)
        
        # create arc
        self.create_arc(self.padding / 2, self.padding / 2, 
                        self.width - self.padding / 2, self.height - self.padding / 2,
                        start=270, extent=360 * self.percent_done, 
                        width=self.padding, style='arc')
        

        # put label in the center
        self.create_text(self.width / 2, self.height / 2, text=self.label, 
                         fill=self.textcolor, font=('marker felt', 14), 
                         anchor='center')

# my own button with rounded edges
class RoundButton(tk.Canvas):
    def __init__(self, parent, width, height, rad, padding, outline, text, textcolor, command):
        tk.Canvas.__init__(self, parent, borderwidth=0, relief='flat',
                           highlightthickness=0, bg='deep sky blue')
        
        # setup
        self.width = width
        self.height = height
        self.rad = rad
        self.padding = padding
        self.outline = outline
        self.text = text
        self.textcolor = textcolor
        self.command = command
        self.times_clicked = 0

        # draw button, configure width/height, and have button events
        self.draw()
        dims = self.bbox('all')
        self.configure(width=dims[2] - dims[0], height=dims[3] - dims[1])
        self.bind('<ButtonPress-1>', self.clicked)
        self.bind('<ButtonRelease-1>', self.released)
        self.bind('<Enter>', self.hovered)
        self.bind('<Leave>', self.unhovered)

    def draw(self):
        # non-arc part
        self.create_polygon((self.padding, self.height - self.rad - self.padding,
                             self.padding, self.rad + self.padding,
                             self.padding + self.rad, self.padding,
                             self.width - self.padding - self.rad, self.padding,
                             self.width - self.padding, self.rad + self.padding,
                             self.width - self.padding, self.height - self.rad - self.padding,
                             self.width - self.padding - self.rad, self.height - self.padding,
                             self.padding + self.rad, self.height - self.padding), 
                             fill=self.outline, outline=self.outline)
        
        # top left arc
        self.create_arc((self.padding, self.padding + 2 * self.rad,
                         self.padding + 2 * self.rad, self.padding), 
                         start=90, extent=90, fill=self.outline, outline=self.outline)
        
        # top right arc
        self.create_arc((self.width - self.padding - 2 * self.rad, self.padding, 
                         self.width - self.padding, self.padding + 2 * self.rad), 
                         start=0, extent=90, fill=self.outline, outline=self.outline)

        # bottom right arc
        self.create_arc((self.width - self.padding, self.height - 2 * self.rad - self.padding,
                         self.width - self.padding - 2 * self.rad, self.height - self.padding), 
                         start=270, extent=90, fill=self.outline, outline=self.outline)
        
        # bottom left arc
        self.create_arc((self.padding, self.height - self.padding - 2 * self.rad,
                         self.padding + 2 * self.rad, self.height - self.padding), 
                         start=180, extent=90, fill=self.outline, outline=self.outline)
        
        # text in the middle
        self.create_text((self.width/2, self.height/2), 
                         fill=self.textcolor, font=('marker felt', 16), 
                         text=self.text, anchor=tk.CENTER)
    
    # button events

    def clicked(self, event): 
        self.configure(relief='sunken')
        self.times_clicked += 1

    def released(self, event): 
        self.configure(relief='raised')
        self.command()

    def hovered(self, event):
        self.prev_outline = self.outline
        self.outline = 'peach puff'
        self.draw()
    
    def unhovered(self, event):
        self.outline = self.prev_outline
        self.draw()

# my own frame that has a border and a label at the top 
class NiceFrame(tk.Canvas):
    def __init__(self, parent, width, height, padding, outline, label, textcolor, bg):
        tk.Canvas.__init__(self, parent, borderwidth=0, bg=bg, relief='flat',
                           highlightthickness=0, width=width, height=height)
        # setup
        self.padding = padding
        self.width = width
        self.height = height
        self.bg = bg
        self.outline = outline
        self.label = label
        self.textcolor = textcolor

        # draw
        self.draw()
        self.configure(width=self.width, height=self.height)
    
    def draw(self):
        # draw text at the top of box
        text = self.create_text(self.padding + 25, self.padding + 5, text=self.label, 
                                anchor='w', fill=self.textcolor, 
                                font=('marker felt', 14))
        dims = self.bbox(text) # get "length" of the text

        # make the border
        self.create_line((self.padding + 20, self.padding + 5,
                          self.padding, self.padding + 5,
                          self.padding, self.height - self.padding,
                          self.width - self.padding, self.height - self.padding,
                          self.width - self.padding, self.padding + 5,
                          self.padding + 25 + dims[2] - dims[0], self.padding + 5),
                          fill=self.outline, width=3)