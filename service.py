# Written by Alex Corbett, Feb 2024

### This will be the service .py file running on the on-board RPi so as long as it is turned on

## CURRENTLY WORKING ON:

# 1. Explore parallel programming. Have a message listening "parent" that will spit out "child" functions. Parent, child, and other childs would all run on different threads
# i.e. a child could be made when client specifies in the json string that they want a live feed of the tcam, the child would then run that until parent tells it to stop.
# Parent will tell it to stop when client says so in their json string (parent is constantly listening and assigning tasks to different threads) - NEED TO DO THIS PROPERLY THOUGH https://superfastpython.com/safely-stop-a-process-in-python/  
# Meanwhile, another child could be handling a command request. This allows live view from the tcam while a command or data request is being carried out (theoretically)

# 2. (maybe) Creating some kind of log file on Pi locally for testing purposes. All printed statements and error catches would be useful to append to log

from datetime import datetime
import time
import socket
import json
from multiprocessing import Process, managers
import numpy as np
from funcs import *
# machine for rpi <-> r pico (requesting payload data). probably i2c or something. However, the pico will also be connected via i2c to the amg88xx
#import RPi.GPIO as GPIO


# CLIENT PROCESSES
# 1. Default. User input() OR menu system for messages to server. Starts 2 once message is sent. Time wait before can send next message? Can only send one request at a time
# 2. Listening for recieved messages and distributing to other processes below. If "TCAM stream" json, send to 3. If "data snapshot" json, send to 4.
# 3. Plot TCAM data from recieved json string
# 4. Parse recieved data or snapshot of TCAM to determine evacuation areas. For TCAM snapshot, need to write a .txt with columns "location", "temp", "safe or evacuate?" for all locations

# SERVER PROCESSES
# 1. Default. Waits for connection from client. If it's a command, start process 2. If data req, start process 3. If live TCAM stream (TRUE), start process 4. If live TCAM stream (FALSE), safely end process 4. If shutdown, run shutdown function on this process, ensuring other processes are shut down safely.
# 2. Command specific process function
# 3. Data request function
# 4. Live TCAM stream function


#### PROCESS 1 - MAIN BODY 

# Setting up server. Will need to add try excepts here if anything goes wrong
# Based on https://www.youtube.com/watch?v=79dlpK03t30&list=PLGs0VKk2DiYxdMjCJmcP6jt4Yw6OHK85O&index=48
buffersize = 1024
server_ip = str(socket.gethostbyname(socket.gethostname()))     # String or no string?
server_port = 2222
RPIServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
RPIServer.bind((server_ip,server_port))
print("Server is running under IP ",server_ip," and port ",server_port)

data_list=["TCAM","VOLT","TEMP"] # For additional intentifiable data reqs, add them here and then add them to parse_data() in funcs.py!!!!!!
cmmd_list=["AOCS","CMD2","CMD3"] # For additional intentifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!

# Queue for managing multiprocesses
q_mgr = managers.SyncManager()
q_mgr.start()

while True:
    data = {}   # Dictionary later to be converted to json and sent to client
    
    #Initial message handling and acknowledgement
    msg,ip = RPIServer.recvfrom(buffersize)     #https://stackoverflow.com/questions/7962531/socket-return-1-but-errno-0 if no message recieved?    #or does it wait?
    msg = json.loads(msg) 
    #msg = json.loads(json.dumps({"TCAM":True,"Voltage":False}))    #for testing
    now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    acknowl = "msg: " + msg + " recieved from " + ip + " at " + now_rec
    print(acknowl)
    RPIServer.sendto(bytes(acknowl, "utf-8"),ip)  #quick response to client to say server has recieved msg
    print("Acknowledgement sent to " + ip)
    
    # Message decoding
    keysList = list(msg.keys())

    # Determining request type - should they be elifs?
    if ((len(keysList)==1) and (keysList[0] == "SHUTDOWN")):    # SHUTDOWN
        if p2.is_alive() == False:
            print("Error: please shutdown TCAM STREAM first")
            RPIServer.sendto(bytes("Error: please shutdown TCAM STREAM first", "utf-8"),ip)
        elif p2.is_alive() == False:
            print("Shutting down in...")
            RPIServer.sendto(bytes("Shutting down in...", "utf-8"),ip)
            time.sleep(1)
            print("3")
            RPIServer.sendto(bytes("3", "utf-8"),ip)
            time.sleep(1)
            print("2")
            RPIServer.sendto(bytes("2", "utf-8"),ip)
            time.sleep(1)
            print("1")
            RPIServer.sendto(bytes("1", "utf-8"),ip)
            time.sleep(1)
            RPIServer.shutdown(socket.SHUT_RDWR)
            RPIServer.close()
            print("Server has shutdown")
        else:
            print("Error: failed to determine TCAM STREAM is_alive()")
            RPIServer.sendto(bytes("Error: failed to determine TCAM STREAM is_alive()", "utf-8"),ip)
        
        # I think this should stay on 1st process P1. Not much point writing function for this in funcs.py?

        # Wait for data and cmd processes to finish if still runing (something like for _ in range(10): if still running: sleep(10), else: shutdown. After loop, give up and just force shutdown other processes)

        # use time sleep to count down? Maybe send this countdown to client as well
        # power off rpi safely as everything is connected to it
        # Need to shutdown any other processes happening
        # not sure on the best way to do this yet
        # Break? if neccessary
    
    elif ((len(keysList) == 1) and (len(keysList[0])==4)):    # COMMAND json: {"CMMD":(param1,param2,param3)}
        parse_cmd(msg,cmmd_list,ip,RPIServer)    # also handles unidentified cmds
        print("parse_cmd()")

    elif (len(keysList) == len(data_list)):    # DATA json: {"DATA":True,"DATA":False,.... for all data in data_list}
        parse_data(msg,ip,RPIServer)     # also handles unidentified data requests
        print("parse_data()")

    elif ((len(keysList)==1) and (keysList[0] == "STREAM")):    # TCAM STREAM json:{"STREAM":True/False}
        if msg["STREAM"] == True:
            if p2.is_alive() == False:
                # Turn on TCAM, start process
                toggle_q = q_mgr.Queue(-1)  # Setting up queue for msg exchange between p1 and p2
                p2 = Process(name="StreamProcess",target=live_tcam,args=(True,ip,RPIServer))       # Setting up p2
                p2.start()  # Starting p2
                print("Starting TCAM STREAM")
            elif p2.is_alive() == True:
                print("Error: TCAM STREAM already running")
            else:
                print("Error: failed to determine TCAM STREAM is_alive()")
            
        elif msg["STREAM"] == False:
            if p2.is_alive() == True:
                # end process
                toggle_q.put(False)
                print("Turning off TCAM STREAM")  
            elif p2.is_alive() == False:
                print("Error: TCAM STREAM already not running")
               

        else:
            acknowl = "Unidentified STREAM command: " + msg
            print(acknowl)   
            RPIServer.sendto(bytes(acknowl, "utf-8"),ip)  # Telling client it's unidentified stream command
    else:
        acknowl = "Unidentified message: " + msg
        print(acknowl)   
        RPIServer.sendto(bytes(acknowl, "utf-8"),ip)  # Telling client it's a completely unidentified message
