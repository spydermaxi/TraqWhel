'''
If you know the size you want and have it you do:
'''

root = # Your root window
myFrame = ttk.Frame(root, height=desiredHeight, width=desiredWidth)
myFrame.pack()

'''
So if you want it relative to the root:
'''

root = # Your root window
rootHeight = root.winfo_height()
rootWidth = root.winfo_width()
# Say you want it to be 20 pixels smaller
myFrame = ttk.Frame(root, height=rootHeight-20, width=rootWidth-20)
myFrame.pack()
# OR
myFrame = ttk.Frame(root) # No set dimensions
myFrame.pack(padx=20, pady=20)
# This will make it have a padding of 20 pixels on height and width,
# with respect to parent rather than itself

'''
You can also force an update right away without entering your mainloop, by using something like this:
'''

root = Tk()
# set up widgets here, do your grid/pack/place
# root.geometry() will return '1x1+0+0' here
root.update()
# now root.geometry() returns valid size/placement
root.minsize(root.winfo_width(), root.winfo_height())

'''
Description of update() at effbot tkinterbook:
Processes all pending events, calls event callbacks, completes any pending geometry management, redraws widgets as necessary, and calls all pending idle tasks. This method should be used with care, since it may lead to really nasty race conditions if called from the wrong place (from within an event callback, for example, or from a function that can in any way be called from an event callback, etc.). When in doubt, use update_idletasks instead.
I've used this a good deal while messing about trying to figure out how to do things like get the size/position of widgets before jumping into the main loop.
'''
