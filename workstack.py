#########################################################
#	     *Simple Multiprocess Workstack*            #
#	      Originally by Lukas Mittnacht             #
#	      2017 for running C-Code to solve          #
#	      Boltzmann-Equations for different         #
#	      Parameter Points				#
#	      ---> Adapted to run CosmoTransitions      #
#########################################################

import os
import subprocess as sp
import linecache
import sys
import time
import numpy as np

#Some needed variables
#indirectory = "sortedsmall"
logdir = "logs"
stdout = "out"
allfiles = []
workstack = []
logstack = []
running = []
idlelist = []
totalwork = 0

#Defines the maximal amount of subprocesses spawned 
maxproc = 8 

#Define Parameterspaces
msmin = 100
msmax = 100
msstep = 10

lmdamin = 0.5
lmdamax = 2
lmdastep = 0.1
lmdalist = np.arange(lmdamin,lmdamax+lmdastep,lmdastep)


#Draw nice updating progressbar
def update_progress(progress,total,hashes = 50):
    sys.stdout.write('\r[{0}] {1}%'.format('#'*int(progress/total * hashes) + '.'*int(hashes -  progress/total * hashes), round(progress/total *100)))

#Get all the Tracefiles in $indirectory
#for filename in os.listdir(indirectory):
#	if filename.endswith(".txt") and filename.startswith("ms"): 
#		allfiles.append(filename)

#Fill the workstack
for l in lmdalist:
	for m in range(msmin,msmax+1,msstep):
		workstack.append(["./RunCosmoTransitions.py","-m",str(m), "-l",str(l)])
		logstack.append(logdir+"/m_"+str(m)+"_l_"+str(l)+"_log.txt")
totalwork = len(workstack)

#Initialize Idlelist
for i in range(maxproc):
	idlelist.append(0)

print("In total "+str(totalwork)+" jobs to run, will launch at most " + str(maxproc) + " processes at the same time\n")
#print(workstack)
done = False
logfiles = []
#Work until workstack is empty
update_progress(0,totalwork)
while (done == False):

	if (len(workstack)>0):		
		#Spawn subprocesses
		while(len(running)<maxproc) and len(workstack)>0:
			currlog = logstack.pop()
			logfile = open(currlog,'w')
			logfiles.append(logfile)		
			running.append(sp.Popen(workstack.pop(),shell=False,stdout=logfile,stderr=sp.DEVNULL))

	#Give Processor some breathing time			
	time.sleep(0.1)
		
	#Check for finished processes
	for i in range (len(running)):
		if running[i].poll() != None:
			idlelist[i]= 1
	
	#Remove finished processes from running list
	popcounter = 0 

	for i in range(maxproc):
		if idlelist[i] ==  1:
			running.pop(i-popcounter)
			idlelist[i] = 0
			popcounter +=1				
			update_progress(totalwork-len(workstack)-len(running),totalwork)		
	if (len(workstack)==0 and len(running)==0): done = True

#FIXME Very bad style keeping all those files open until the end
#Can be fixed by checking the running list for the handles associated with the logfile
#if handle is no longer present then close the file
#NOTE TOO LAZY TO IMPLEMENT NOW ---> LATER IF NECCESSARY
for log in logfiles: log.close()	
		
		
