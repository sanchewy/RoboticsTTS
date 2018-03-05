from serial import *
from sys import version_info
import time
import Maestro

class Done(Exception): pass

class Instruction():
    flag = True

    def __init__(self, target, target_val=6000, run_time=1):
        self.target = target
        self.target_val = target_val
        self.run_time = run_time

    def setTargetVal(self, target_val):
        self.target_val = target_val
    
    def setRunTime(self, run_time):
        self.run_time = run_time

    def changePos(self, array_pos):
        instruct_arr[self.array_pos] = None
        instruct_arr[array_pos] = self
        self.array_pos = array_pos

    def runInstruction(self, maestro):
        maestro.setTarget(self.target, self.target_val)
        time.sleep(self.run_time)
        slowDown(self.target, self.target_val, maestro)

def getInstruction():
    i = 0
    while Instruction.instruct_arr[i] != None:
        i = i + 1

    user_in = input("Instruction: ")

    # Add instruction to Instruction array
    if user_in == "move":
        Instruction.instruct_arr[i] = Instruction(i, 1, target_val=6000)
    elif user_in == "turn":
        Instruction.instruct_arr[i] = Instruction(i, 2, target_val=6000, run_time=1.5)
    elif user_in == "quit":
        Instruction.flag = False
        raise Done

    # Change instruction values
    else:
        split = user_in.split(' ')
        inst = Instruction.instruct_arr[(int)(split[0])]
        val = (int)(split[2])

        if split[1] == "setTargetVal":
            inst.setTargetVal(val)

        elif split[1] == "setRunTime":
            inst.setRunTime(val)


increment = 250
#Slow down motion on servo X going curSpeed by increment
def slowDown(servo, curSpeed, maestro):
    if(servo == 1 or servo ==2):
        forward = curSpeed < 6000
        timeDelay = .05
        decrementSpeed = curSpeed
        if(forward):
            while(decrementSpeed < 6000):
                decrementSpeed = decrementSpeed + increment
                maestro.setTarget(servo, decrementSpeed)
                time.sleep(timeDelay)
            maestro.setTarget(servo, 6000)
        else:
            while(decrementSpeed > 6000):
                decrementSpeed = decrementSpeed - increment
                maestro.setTarget(servo, decrementSpeed)
                time.sleep(timeDelay)
            maestro.setTarget(servo, 6000)

if __name__ == '__main__':

    stdval = 6000
    curvalFB = 6000
    curvalLR = 6000
    headtilt = 6000
    headturn = 6000

    x = Maestro.Controller()
    x.setTarget(0, stdval)
    x.setTarget(1, stdval)
    x.setTarget(2, stdval)
    x.setTarget(3, stdval)
    x.setTarget(4, stdval)
    
#    print("List of instructions:")
#    print("Move:    move")
#    print("Turn:    turn")
#    print("Quit:    quit")
#    print()
#    print("Change target_val:   n setTargetVal n")
#    print("Change run_time:     n setRunTime n")

    while Instruction.flag:
        try:
            # Break from while loop if we have 8 instructions
            for i in range(8):
                if Instruction.instruct_arr[i] == None:
                    break
                if i == 7:
                    raise Done

            getInstruction()

        except Done:
            break

    runInstructions(x)
    
    x.setTarget(0, stdval)
    slowDown(1, curvalFB)
    slowDown(2, curvalLR)
    x.setTarget(3, stdval)
    x.setTarget(4, stdval)

