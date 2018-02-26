import sys
from multiprocessing.dummy import Process
import time

def printHello(numTimes):
	print("Hello " + str(numTimes))

def delay(sec):
	for x in range(sec):
		time.sleep(1)
		# print("Delay one second")


p = Process(target=delay, args=(5 ,))
p.start()
print("Process alive: " + str(p.is_alive()))
map(printHello, range(20))
while(p.is_alive()):
	pass
print("Exit code: " + str(p.exitcode))
