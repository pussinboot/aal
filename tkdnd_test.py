# from
# http://stackoverflow.com/questions/17698138/python-gui-programming-using-drag-and-drop-also-incorporating-stdout-redirect?lq=1

import os
from tkinter import *

import tkinter
from tkdnd_wrapper import TkDND


class Redir(object):
    # This is what we're using for the redirect, it needs a text box
    def __init__(self, textbox):
        self.textbox = textbox
        self.textbox.config(state=NORMAL)
        self.fileno = sys.stdout.fileno

    def write(self, message):
        # When you set this up as redirect it needs a write method as the
        # stdin/out will be looking to write to somewhere!
        self.textbox.insert(END, str(message))

root = tkinter.Tk()

dnd = TkDND(root)

textbox = tkinter.Text()
textbox.pack()

def handle(event):
    event.widget.insert(END, event.data)
    content = textbox.get("0.0",tkinter.END)
    filename = content.split()

dnd.bindtarget(textbox, handle, 'text/uri-list')

#Set up the redirect 
stdre = Redir(textbox)
# Redirect stdout, stdout is where the standard messages are ouput
sys.stdout = stdre
# Redirect stderr, stderr is where the errors are printed too!
sys.stderr = stdre
# Print hello so we can see the redirect is working!
print ("hello")
# Start the application mainloop
root.mainloop()