"""
This code demonstrates "bare bones" drag and drop
"""
import sys
import platform

try:
    # for Python2
    from Tkinter import *  ## notice capitalized T in Tkinter 
except ImportError:
    # for Python3
    from tkinter import *  ## notice lowercase 't' in tkinter here
try:
    import Tkdnd
except ImportError:
    import tkinter.dnd as Tkdnd
    
SERVO_TOP = 9000
SERVO_BOTTOM = 3000
STEP_SIZE = 500

frame_dict = {}     #I had to make this global ABOVE execute_instructions(). Other Tkinter methods managed to find the dict out of scope, but execute_instructions threw a fit about it.

class Dragged:
    """
    This is a thing to be dragged and dropped.
    """
    def __init__(self, button):
        self.button = button
        print("An instance of Dragged has been created for button %s" % (button))
        
    def dnd_end(self,Target,Event):
        #this gets called when we are dropped
        print("I have been dropped; Target=%s" % ('Target'))

#Not currently being used (see FrameDnd)
class CanvasDnd(Canvas):
    """
    This is a canvas to which we have added a "dnd_accept" method, so it
    can act as a Target Widget for drag and drop. To prove that the Target
    Object can be different from the Target Widget, CanvasDnd accepts as
    argument "GiveDropTo" the object to which the dropped object is to 
    be given.
    """    
    def __init__(self, Master, GiveDropTo, **kw):
        Canvas.__init__(self, Master, kw)
        #Simply remember the TargetObject for later use.
        self.GiveDropTo = GiveDropTo

    def dnd_accept(self,Source,Event):
        #Tkdnd is asking us if we want to tell it about a TargetObject.
        #We do, so we pass it a reference to the TargetObject which was
        #given to us when we started
        print("Canvas: dnd_accept")
        return self.GiveDropTo

#Enhanced frame object keeps track of list of children and Drop receptor
class FrameDnd(Frame):
    def __init__(self, Master, GiveDropTo, **kw):
        Frame.__init__(self,Master, kw)
        self.GiveDropTo = GiveDropTo
        self.ListChildren = list()

    def dnd_accept(self,Source,Event):
        # print("Frame: is ready to accept dnd.")
        return self.GiveDropTo
    
    def add_child(self,child):
        if(type(child) is list):
            self.ListChildren.extend(child)
        else:
            self.ListChildren.append(child)

#This implements methods required by the TkDnd library for handling widget DND enter, exit, movement, and dropping (We only care about dropping).
class Receptor:
    """
    This is a thing to act as a TargetObject
    """
    def dnd_enter(self,Source,Event):
        #This is called when the mouse pointer goes from outside the
        #Target Widget to inside the Target Widget.
        # print ("Receptor: dnd_enter")
        pass
        
    def dnd_leave(self,Source,Event):
        #This is called when the mouse pointer goes from inside the
        #Target Widget to outside the Target Widget.
        # print ("Receptor: dnd_leave")
        pass
        
    def dnd_motion(self,Source,Event):
        #This is called when the mouse pointer moves withing the TargetWidget.
        # print ("Receptor: dnd_motion")
        pass
        
    def dnd_commit(self,Source,Event):
        #This is called if the DraggedObject is being dropped on us
        print ("Receptor: dnd_commit; Object received = %s" % str(Source))
        print("Accepting Frame Number = %s" % str(get_frame_num(Event.x)))
        print("Location: "+str(Event.x))
        # print(dir(Source))
        # print(Source.__class__)
        if isinstance(Source, Dragged):
            print("Received object is an instance of Dragged.class from button %s" % (Event.widget.cget('text')))
            if(get_frame_num(Event.x) in frame_dict and not frame_dict.get(get_frame_num(Event.x)).ListChildren):     # If there are children in frame, it already contains an instruction
                create_instruction_frame(get_frame_num(Event.x), Event.widget.cget('text'))
            else:
                print("Error, Invalid drop at x_coor: %s" % (str(Event.x)))
        else:
            print("Error: Received object was not an instance of Dragged.class.")

#Creates instruction frame with label name and remove and edit buttons at Frame<frame_num>
def create_instruction_frame(frame_num, button_name):
    frame = frame_dict.get(frame_num)
    lab = Label(frame, text=button_name+" Command", fg='blue', wraplength=75)
    lab.pack()
    # print(">>> %s <<<" % (str(type(lab))))
    remove = Button(frame, text='Remove')
    remove.pack()
    remove.bind('<ButtonPress>',lambda event: remove_frame_children(event, frame))
    edit = Button(frame, text='Edit')
    edit.pack()
    edit.bind('<ButtonPress>', lambda event: settings_popup(event, frame))
    frame.add_child([lab,remove,edit]) # add children to list in Frame (so that we can delete them later without deleting the entire frame)

#Destroys each child widget passed    
def remove_frame_children(Event, frame):
    for child in frame.ListChildren:
        child.destroy()
    del frame.ListChildren[:]
        
#Creates a popup toplevel window for editing the settings of the instruction corresponding to frame.
def settings_popup(Event, frame):
    widget_list = list()    #Use on toplevel window close to 'get()' all the slider properties and pass them to frame.instruction
    toplevel = Toplevel()    
    toplevel.protocol("WM_DELETE_WINDOW", lambda: extract_instructions(frame, widget_list, toplevel))
    toplevel.geometry("600x300+%d+%d" % (Root.winfo_x(), Root.winfo_y()))    
    instruct_type = frame.ListChildren[0].cget('text')
    label1 = Label(toplevel, text="Popup window for frame type "+instruct_type)
    label1.pack()
    
    #  print(">>> %s <<<" % (str(instruct_type)))
    if(instruct_type == "Pause Command"):
        slider = Scale(toplevel, from_=0, to_=5, orient=HORIZONTAL, label='Pause Len:', length=200)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "BodyTurn Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Body Turn To:', length=500)
        slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "HeadTurn Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Head Turn To:', length=500)
        slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "HeadTilt Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Head Tilt To:', length=500)
        slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "Motors Command"):
        v = IntVar()
        rb1 = Radiobutton(toplevel, text="Turn", padx = 20, variable=v, value=1)
        rb1.pack()
        rb2 = Radiobutton(toplevel, text="Forward/Backward",padx = 20, variable=v, value=2)
        rb2.pack()
        print(v.get())
        if(v.get()==2):
            print("2222")
        elif(v.get()==1):
            print("1111")
        else:
            print("Error: Radio button selection was neither choice?")
        
    else:
        print("Error: Unrecognized instruction type: " + str(instruct_type))
        
#Get values from sliders and buttons to set the instruction parameters for the given frame
def extract_instructions(frame, widget_list, window):
    for wid in widget_list:
        sys.stdout.write("Window had widget of type: %s" % str(type(wid)))
        if isinstance(wid, Scale):
            sys.stdout.write(" with slider value: "+str(wid.get()))
        sys.stdout.write('\n')
    window.destroy()

#Hard coded x coordinates of each Frame to determine drop location of widget
def get_frame_num(x_coor):
    win_increment = (0,0)
    if(platform.system() == 'Windows'):
        win_increment = (15,10)
    if(x_coor > 95 - win_increment[0] and x_coor <= 165 - win_increment[1]): #80 - 155
        return 1
    elif(x_coor > 175 - win_increment[0] and x_coor <= 250 - win_increment[1]): #165 - 240
        return 2
    elif(x_coor > 260 - win_increment[0] and x_coor <= 335 - win_increment[1]):
        return 3
    elif(x_coor > 345 - win_increment[0] and x_coor <= 420 - win_increment[1]):
        return 4
    elif(x_coor > 430 - win_increment[0] and x_coor <= 505 - win_increment[1]):
        return 5
    elif(x_coor > 515 - win_increment[0] and x_coor <= 590 - win_increment[1]):
        return 6
    elif(x_coor > 600 - win_increment[0] and x_coor <= 675 - win_increment[1]):
        return 7
    elif(x_coor > 685 - win_increment[0] and x_coor <= 765 - win_increment[1]):
        return 8
    else:
        return -1

#Creates a draggable button object
def on_dnd_start(Event, button):
    """
    This is invoked by InitiationObject to start the drag and drop process
    """
    #Create an object to be dragged
    ThingToDrag = Dragged(button)
    
    #Pass the object to be dragged and the event to Tkdnd
    Tkdnd.dnd_start(ThingToDrag,Event)

def execute_instructions(Event):
    #TODO: Start Multi thread graphic to show that the program is running.
    print("items: "+str(frame_dict.items()))
    for key,value in frame_dict.items():
        #TODO: Something like "value.instruction.execute()"
        #TODO: Decide what to do if a frame doesn't have an instruction (blank frame). We could probably just skip it.
        print("Executing Instructions for frame: " + str(key))

Root = Tk()
Root.title('Robot Touch Controls')
Root.geometry('800x600')
#Create an object whose job is to act as a TargetObject, that is, to
# received the dropped object.
TargetObject = Receptor()

Start = Button(Root,text='Start', height=2,width=10)
Start.pack(side=BOTTOM, pady=50)
Start.bind('<ButtonPress>', execute_instructions)

#Create a button to act as the InitiationObject and bind it to <ButtonPress> so
# we start drag and drop when the user clicks on it.
frame = Frame(Root, width=100, height = 200)
frame.pack_propagate(False)
frame.pack(side = LEFT, padx=5)

#Create all the left-hand-side instruction option buttons
Motors = Button(frame,text='Motors')
Motors.pack(fill='x',side=BOTTOM)
Motors.bind('<ButtonPress>', lambda event: on_dnd_start(event, 'Motors'))
HeadTilt = Button(frame,text='HeadTilt')
HeadTilt.pack(fill='x',side=BOTTOM)
HeadTilt.bind('<ButtonPress>', lambda event: on_dnd_start(event, 'HeadTilt'))
HeadTurn = Button(frame,text='HeadTurn')
HeadTurn.pack(fill='x',side=BOTTOM)
HeadTurn.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'HeadTurn'))
BodyTurn = Button(frame,text='BodyTurn')
BodyTurn.pack(fill='x',side=BOTTOM)
BodyTurn.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'BodyTurn'))
Pause = Button(frame,text='Pause')
Pause.pack(fill='x',side=BOTTOM)
Pause.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'Pause'))
Label(frame, text="Commands", fg='blue').pack(side=BOTTOM)

#Create all right-hand-side frame rectangles, set them to give drops to TargetObject (Receptor()), and add them to dictionary for coordinate lookup
frame1 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame1.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame1.pack_propagate(False)
frame2 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame2.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame2.pack_propagate(False)
frame3 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame3.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame3.pack_propagate(False)
frame4 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame4.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame4.pack_propagate(False)
frame5 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame5.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame5.pack_propagate(False)
frame6 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame6.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame6.pack_propagate(False)
frame7 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame7.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame7.pack_propagate(False)
frame8 = FrameDnd(Root,width=75, height = 200, GiveDropTo=TargetObject,relief=RAISED, borderwidth=2)
frame8.pack(side = LEFT,expand=NO,fill=None,padx=5)
frame8.pack_propagate(False)

frame_dict = {1:frame1,2:frame2,3:frame3,4:frame4,5:frame5,6:frame6,7:frame7,8:frame8}

#Begin main program loop
Root.mainloop()
