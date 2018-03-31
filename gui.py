"""
This code demonstrates "bare bones" drag and drop
"""
from sys import *
from platform import *

import PIL.Image
import time
import threading
import touch_ctrl
import Maestro

import ClientThread
import ServerThread

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
PORT = ""
ADDRESS = ""

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
        #TODO: Add self.instruction reference to you instruction object class.
        self.instruction = None

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
        #This is called when the mouse pointer moves within the TargetWidget.
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
    
    #Create remove button
    remove = Button(frame, text='Remove')
    remove.pack()
    remove.bind('<ButtonPress>',lambda event: remove_frame_children(event, frame))
    
    #Create edit button
    edit = Button(frame, text='Edit')
    edit.pack()
    edit.bind('<ButtonPress>', lambda event: settings_popup(event, frame))
    frame.add_child([lab,remove,edit]) # add children to list in Frame (so that we can delete them later without deleting the entire frame)

	#Create instruction
    if(button_name == "Pause"):
        frame.instruction = touch_ctrl.Instruction(5)
    elif(button_name == "BodyTurn"):
        frame.instruction = touch_ctrl.Instruction(0)
    elif(button_name == "HeadTurn"):
        frame.instruction = touch_ctrl.Instruction(3)
    elif(button_name == "HeadTilt"):
        frame.instruction = touch_ctrl.Instruction(4)
    elif(button_name == "Motors"):
        frame.instruction = touch_ctrl.Instruction(1)
    elif(button_name == x for x in ["Eva","Wall_E","NothingHere","GrowBolts", "Introduce"]):
        frame.instruction = touch_ctrl.Instruction(6)

#Destroys each child widget passed    
def remove_frame_children(Event, frame):
    #Destroy all child widgets
    for child in frame.ListChildren:
        child.destroy()
    #Reset list of children
    del frame.ListChildren[:]
    #TODO: Now you must reset the actual instruction stored in frame.instruction so that it doesn't maintain a reference after removal of GUI frame.
    frame.instruction = None

#Creates a popup toplevel window for editing the settings of the instruction corresponding to frame.
def settings_popup(Event, frame):
    widget_list = list()    #Use on toplevel window close to 'get()' all the slider properties and pass them to frame.instruction
    toplevel = Toplevel()    
    toplevel.protocol("WM_DELETE_WINDOW", lambda: extract_instructions(frame, widget_list, toplevel))  #On popup close, call extract_instructions with frame info and widget_list.
    toplevel.geometry("600x300+%d+%d" % (Root.winfo_x(), Root.winfo_y()))   
    
    #Child[0] is the Label for the frame. So we can determine the type of instruction based on the label. It would have been better to do frame.instruction.type(), but we didn't have that implemented at time of GUI.
    instruct_type = frame.ListChildren[0].cget('text')
    print("Instruction Type: "+ instruct_type)
    label1 = Label(toplevel, text="Popup window for frame type "+instruct_type)
    label1.pack()
    
    #Filters on instuction_type to create an appropriate frame with sliders and buttons for servo values / pause length / motor run time.
    #TODO: If you want, you could reference frame.instruction properties in slider.set() so that the GUI "remembers" what you set the slider to after closing and reopening the settings popup.
    if(instruct_type == "Pause Command"):
        slider = Scale(toplevel, from_=0, to_=5, orient=HORIZONTAL, label='Pause Len:', length=200)
        slider.set(frame.instruction.run_time)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "BodyTurn Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Body Turn To:', length=500)
        #slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        slider.set(frame.instruction.target_val)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "HeadTurn Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Head Turn To:', length=500)
        #slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        slider.set(frame.instruction.target_val)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "HeadTilt Command"):
        slider = Scale(toplevel, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, label='Head Tilt To:', length=500)
        #slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
        slider.set(frame.instruction.target_val)
        widget_list.append(slider)
        slider.pack()
    elif(instruct_type == "Motors Command"):
        v = StringVar()
        v.set("Empty")

        #Called on radio button press. Creates frame below radio buttons with appropriately named sliders. 
        def get_choice():
            #Destroy old frames (when switching the stupid radio button between 'FB' and 'Turn')
            for child in toplevel.winfo_children():
                if isinstance(child, Frame):
                    child.destroy()
            widget_list.clear()
            bonus_frame = Frame(toplevel)
            bonus_frame.pack()
            selection = str(v.get())
            print("Radio Button Choice: "+selection)
            slider = Scale(bonus_frame, from_=SERVO_BOTTOM, to_=SERVO_TOP, tickinterval=STEP_SIZE, orient=HORIZONTAL, length=500)
            #slider.set((SERVO_BOTTOM+SERVO_TOP)/2)
            slider.set(frame.instruction.target_val)
            slider2 = Scale(bonus_frame, from_=0, to_=10, orient=HORIZONTAL, length=500)
            slider.set(frame.instruction.run_time)
            if(selection=="Turn"):
                #Append instruction as a string, to be unpacked in extract_instructions
                widget_list.append("Turn")
                slider.configure(label="Turn Direction")
                slider.pack()
                slider2.configure(label="Turn Seconds")
                slider2.pack()
                widget_list.extend([slider,slider2])
            elif(selection=="FB"):
                #Append instruction as a string, to be unpacked in extract_instructions
                widget_list.append("FB")
                slider.configure(label="Motor Speed")
                slider.pack()
                slider2.configure(label="Seconds of Movement")
                slider2.pack()
                widget_list.extend([slider,slider2])  
            else:
                print("Error: Radio button choice in motoro selection was neither FB or Turn.")
            
        # I did not add these to the widget list because we only need the "turn" "FB" value (which is not contained in the widget).
        rb1 = Radiobutton(toplevel, text="Turn", command=get_choice,padx = 20, variable=v, value="Turn")
        rb1.pack(anchor=W)
        rb2 = Radiobutton(toplevel, text="Forward/Backward",command=get_choice, padx = 20, variable=v, value="FB")
        rb2.pack(anchor=W)
    elif(instruct_type.rsplit(' ', 1)[0] == x for x in ["Eva","Wall_E","NothingHere","GrowBolts", "Introduce"]):
        label2 = Label(toplevel, text="You can't change voice commands!")
        label2.pack()
        widget_list.append(instruct_type.rsplit(' ', 1)[0])
    else:
        print("Error: Unrecognized instruction type: " + str(instruct_type))
        
#Get values from sliders and buttons to set the instruction parameters for the given frame
def extract_instructions(frame, widget_list, window):
    #TODO: Here you know the frame. Do frame.instruction.set(wid.get) to set the servo value.
    print(">>>Extract instructions was called with list size: %s<<<" % (str(len(widget_list))))
    for wid in widget_list:
        sys.stdout.write("Window had widget of type: %s" % str(type(wid)))
        if isinstance(wid, Scale):
            sys.stdout.write(" with slider value: "+str(wid.get()))
            value = wid.get()
            if value < 3000:
                #Set instruction run time
                frame.instruction.run_time = value
            else:
                #Set Maestro servo target value
                frame.instruction.target_val = wid.get()
        elif isinstance(wid, str):
            sys.stdout.write(" with motor operation value: "+wid)
            #Set Maestro servo target
            if wid == "Turn":
                frame.instruction.target = 2
            elif wid == "FB":
                frame.instruction.target = 1
            elif wid == "Eva":
                frame.instruction.target = 6
                frame.instruction.textToSpeak = "Eva"
            elif wid == "Wall_E":
                frame.instruction.target = 6
                frame.instruction.textToSpeak = "Walle"
            elif wid == "NothingHere":
                frame.instruction.target = 6
                frame.instruction.textToSpeak = "There is nothing here"
            elif wid == "GrowBolts":
                frame.instruction.target = 6
                frame.instruction.textToSpeak = "Grow some bolts"
            elif wid == "Introduce":
                frame.instruction.target = 6
                frame.instruction.textToSpeak = "Allow me to introduce myself, I am CL4P-TP"


        sys.stdout.write('\n')  
    window.destroy()

#Hard coded x coordinates of each Frame to determine drop location of widget (Cannot be done simply by referencing the Event)
def get_frame_num(x_coor):
    win_increment = (0,0)
    #if(platform.system() == 'Windows'):
    #    win_increment = (15,10)
    if(x_coor > 110 - win_increment[0] and x_coor <= 185 - win_increment[1]): #80 - 155
        return 1
    elif(x_coor > 195 - win_increment[0] and x_coor <= 270 - win_increment[1]): #165 - 240
        return 2
    elif(x_coor > 280 - win_increment[0] and x_coor <= 355 - win_increment[1]):
        return 3
    elif(x_coor > 365 - win_increment[0] and x_coor <= 440 - win_increment[1]):
        return 4
    elif(x_coor > 450 - win_increment[0] and x_coor <= 525 - win_increment[1]):
        return 5
    elif(x_coor > 535 - win_increment[0] and x_coor <= 610 - win_increment[1]):
        return 6
    elif(x_coor > 620 - win_increment[0] and x_coor <= 695 - win_increment[1]):
        return 7
    elif(x_coor > 705 - win_increment[0] and x_coor <= 780 - win_increment[1]):
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

#Run animation when flag is True
flag = False
running_servo = None

#Triggered on press of 'Start' button in root window. Iterates over frame_dict executes the instruction in each frame.
def execute_instructions():
    #TODO: Start Multi thread graphic to show that the program is running.

    flag = True

    print("items: "+str(frame_dict.items()))
    # x = Maestro.Controller()
    # x.setTarget(0, 6000)
    # x.setTarget(1, 6000)
    # x.setTarget(2, 6000)
    # x.setTarget(3, 6000)
    # x.setTarget(4, 6000)

    #Create network client  
    client = ClientThread.clientSocket(ADDRESS, PORT)
    for key,value in frame_dict.items():
        #TODO: Something like "value.instruction.execute()"
        #TODO: Decide what to do if a frame doesn't have an instruction (blank frame). We could probably just skip it.
        print("Executing Instructions for frame: " + str(key))
        inst = value.instruction
        if inst != None:
            running_servo = inst.target
            if inst.target == 6:
                print("One of them was a 6")
                client.sendMessage(inst.textToSpeak)
            elif inst.target == 5: #If the instruction is Pause
                time.sleep(inst.run_time)
            else:
                inst.runInstruction(x)
                
    # x.setTarget(0, 6000)
    # x.setTarget(1, 6000)
    # x.setTarget(2, 6000)
    # x.setTarget(3, 6000)
    # x.setTarget(4, 6000)

    flag = False

def start_drawing():
    inst_thread = threading.Thread(target=execute_instructions, args=())
    inst_thread.start()

    toplevel = Toplevel()
    toplevel.geometry("800x600+%d+%d" % (Root.winfo_x(), Root.winfo_y()))   

    frames = [PhotoImage(file='running.gif',format = 'gif -index %i' %(i)) for i in range(9)]
    ind = 0
    def update(ind):
        frame = frames[ind]
        ind += 1
        if ind == 9:
            ind = 0
        label.configure(image=frame)
        if not flag:
            pass
            #toplevel.destroy()
        toplevel.after(100, update, ind)
        if(not inst_thread.isAlive()):
            print("Killed window")
            toplevel.destroy()
    label = Label(toplevel)
    label.pack()
    toplevel.after(0, update, 0)

if __name__ == "__main__":
    #Grab Command line arguments for client server configuration
    PORT = int(sys.argv[2])
    ADDRESS = sys.argv[1]

    #Create server thread for listening to android.
    # print(dir(ServeThread))
    server = ServerThread.servSocket(int(PORT))
    server_thread = threading.Thread(target=server.run, args=())
    server_thread.start()

    #Create main tkinter window.
    Root = Tk()
    Root.title('Robot Touch Controls')
    Root.geometry('800x600')

    #Create an object whose job is to act as a TargetObject, that is, to received the dropped object.
    TargetObject = Receptor()

    #Create start button
    Start = Button(Root,text='Start', height=2,width=10)
    Start.pack(side=BOTTOM, pady=50)
    Start.bind('<ButtonPress>', start_drawing)

    #Create a button to act as the InitiationObject and bind it to <ButtonPress> so
    # we start drag and drop when the user clicks on it.
    frame = Frame(Root, width=100, height = 400)
    frame.pack_propagate(False)
    frame.pack(side = LEFT, padx=5)

    #Create all the left-hand-side instruction option buttons and labels
    Label(frame, text="Commands", fg='blue').pack()
    Motors = Button(frame,text='Motors')
    Motors.pack(fill='x')
    Motors.bind('<ButtonPress>', lambda event: on_dnd_start(event, 'Motors'))
    HeadTilt = Button(frame,text='HeadTilt')
    HeadTilt.pack(fill='x')
    HeadTilt.bind('<ButtonPress>', lambda event: on_dnd_start(event, 'HeadTilt'))
    HeadTurn = Button(frame,text='HeadTurn')
    HeadTurn.pack(fill='x')
    HeadTurn.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'HeadTurn'))
    BodyTurn = Button(frame,text='BodyTurn')
    BodyTurn.pack(fill='x')
    BodyTurn.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'BodyTurn'))
    Pause = Button(frame,text='Pause')
    Pause.pack(fill='x',)
    Pause.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'Pause'))
    Wall_E = Button(frame,text='Wall_E')
    Wall_E.pack(fill='x',)
    Wall_E.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'Wall_E'))        #Walle
    Eva = Button(frame,text='Eva')
    Eva.pack(fill='x',)
    Eva.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'Eva'))          #Eva
    NothingHere = Button(frame,text='NothingHere')
    NothingHere.pack(fill='x',)
    NothingHere.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'NothingHere'))      #Nothing here
    GrowBolts = Button(frame,text='GrowBolts')
    GrowBolts.pack(fill='x',)
    GrowBolts.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'GrowBolts'))      #Grow some bolts
    Introduce = Button(frame,text='Introduce')
    Introduce.pack(fill='x',)
    Introduce.bind('<ButtonPress>',lambda event: on_dnd_start(event, 'Introduce'))      #Allow me to introduce myself, I am CL4P-TP

    #Create all right-hand-side frame rectangles, set them to give drops to TargetObject (Receptor()), and add them to dictionary for coordinate lookup through get_frame_num
    frame1 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame1.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame1.pack_propagate(False)
    frame2 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame2.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame2.pack_propagate(False)
    frame3 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame3.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame3.pack_propagate(False)
    frame4 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame4.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame4.pack_propagate(False)
    frame5 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame5.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame5.pack_propagate(False)
    frame6 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame6.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame6.pack_propagate(False)
    frame7 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame7.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame7.pack_propagate(False)
    frame8 = FrameDnd(Root, width=75, height = 200, GiveDropTo=TargetObject, relief=RAISED, borderwidth=2)
    frame8.pack(side = LEFT,expand=NO,fill=None,padx=5)
    frame8.pack_propagate(False)

    frame_dict = {1:frame1,2:frame2,3:frame3,4:frame4,5:frame5,6:frame6,7:frame7,8:frame8}

    #Begin main program loop
    Root.mainloop()
