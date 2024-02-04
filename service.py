# Written by Alex Corbett, Feb 2024

### This will be the service .py file running on the on-board RPi so as long as it is turned on

## CURRENTLY WORKING ON:
# 1. Changing message syntax to a json string. This makes it easier to identify an incorrect/unidentifable message

# 2. Explore parallel programming. Have a message listening "parent" that will spit out "child" functions. Parent, child, and other childs would all run on different threads
# i.e. a child could be made when client specifies in the json string that they want a live feed of the tcam, the child would then run that until parent tells it to stop.
# Parent will tell it to stop when client says so in their json string (parent is constantly listening and assigning tasks to different threads) - NEED TO DO THIS PROPERLY THOUGH https://superfastpython.com/safely-stop-a-process-in-python/  
# Meanwhile, another child could be handling a command request. This allows live view from the tcam while a command or data request is being carried out (theoretically)

from datetime import datetime
import time
import socket
import json
import multiprocessing as process
import numpy as np
import funcs
# machine for rpi <-> r pico (requesting payload data). probably i2c or something. However, the pico will also be connected via i2c to the amg88xx
#import RPi.GPIO as GPIO

# CLIENT PROCESSES
# 1. Default. User input() OR menu system for messages to server. Starts 2 once message is sent. Time wait before can send next message? Can only send one request at a time
# 2. Listening for recieved messages and distributing to other processes below. If "TCAM stream" json, send to 3. If "data snapshot" json, send to 4.
# 3. Plot TCAM data from recieved json string
# 4. Parse recieved data or snapshot of TCAM to determine evacuation areas. For TCAM snapshot, need to write a .txt with columns "location", "temp", "safe or evacuate?" for all locations

# notes: will need a "TCAM stream" identifier for incoming JSON. Maybe just have one key:value pair or have the first one be called "stream" or something?
# and likewise for "data snapshot"

# SERVER PROCESSES
# 1. Default. Waits for connection from client. If "cmd" is json "key", start process 2. If 
# 2. command specific process function
# 3. Data request function


#### PROCESS 1 - MAIN BODY 

# Setting up server. Will need to add try excepts here if anything goes wrong
# Based on https://www.youtube.com/watch?v=79dlpK03t30&list=PLGs0VKk2DiYxdMjCJmcP6jt4Yw6OHK85O&index=48
buffersize = 1024
server_ip = str(socket.gethostbyname(socket.gethostname()))     # String or no string?
server_port = 2222
RPIServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
RPIServer.bind((server_ip,server_port))
print("Server is running under IP ",server_ip," and port ",server_port)

# EVERYTHING BELOW HERE NEEDS REWRITING

while True:
    data = {}   # Dictionary later to be converted to json and sent to client
    
    #Getting initial message
    msg,ip = RPIServer.recvfrom(buffersize)     #https://stackoverflow.com/questions/7962531/socket-return-1-but-errno-0 if no message recieved?
    msg = msg.decode('utf-8')
    #msg = "cmd:None.data:temp()"    #example msg

    # test if received a message, not sure exactly how to do this yet (this will need another indentation I think?)
     # change this to sucessful message check. might be worth adding try except here too for error catching (ie poff cmd msg includes data request)
        # get current time after msg recieve success 
    

    # may also be worth creating a log file on Pi locally for testing purposes. Printed statement above would be useful to append to log

    if msg == "cmd:poff":      #THIS NEEDS TO HAPPEN FIRST I THINK - would mean cant request info if powering off        
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data.update({"time_rec":now_rec})
        print(msg, + " received from" + ip + "at " + now_rec)
        
        print("Powering off in 3,2,1...") # Maybe send this to client as well, use time to count down
        #power off rpi as everything is connected to it
        # Break? if neccessary
        # not sure on the best way to do this yet

    # Live TCAM Request (to be implimented later down the line)
    elif msg == "cmd:live":   # Might want to add this capability later down the line (this is v advanced)
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data.update({"time_rec":now_rec})
        print(msg, + " received from" + ip + "at " + now_rec)

        print("streaming tcam...")  #send this to client?

        #while ...
            # will be a while (requirement), which also listens for secondary messages inside loop at each update. 
            # Must send (somehow) TCAM array back to client at a regular time intervals (csv? not sure how streaming works through)
            # If a secondary command says stop, it must exit while loop


        # dont want to do any more parsing after exiting this, so either:
        #break 
        # OR override cmd_reqs and data_reqs like this: (so that command and data parsing doesnt happen / just returns "None")
        cmd_reqs = ["None"]
        data_reqs = ["None"]
    else:
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data.update({"time_rec":now_rec})
        print(msg, + " received from" + ip + "at " + now_rec)
        
        # Extract cmds and data requests
        try:
            cmd_reqs = msg.split(".")[0].split(":")[1].split(",")   #string list of 'func(params)'. this should work even if cmd:None only
            data_reqs = msg.split(".")[1].split(":")[1].split(",")  #string list of 'data(params)'. "..."
        except IndexError:  # THIS DOES NOT CAPTURE ALL UNIDENTIFIED COMMANDS! converting client -> server message into json string would be better
            print("Unidentified command")
            data.update({"msg":False})
            
            # ENCODE JSON
            # HERE?
            # Might not be a good idea

            continue    # start while true loop again

        else:   # Success!

            # Deal with commands before data
            cmd_status={}
            if cmd_reqs[0][0:3] == "None":  # first, test if None
                cmd_status.update({"cmd":"none"}) 
                data.update({"cmd_updates":cmd_status}) # dictionary inside data dictionary specifying cmd info
            else:
                for cmd in cmd_reqs:
                    cmd_status.update({cmd: parse_cmd(cmd[0:3],cmd.split("(")[1].split(")")[0],cmd_list) })  # calling parse_cmd() to run command and get cmd success/failure info
                data.update({"cmd_updates":cmd_status}) # dictionary inside data dictionary specifying cmd info


            # Deal with data requests next
            if data_reqs[0][0:3] == "None":  # first, test if None
                data.update({"data":"none"})
            else:
                for data_req in data_reqs:
                    data.update({data_req: parse_data(data_req,data_req.split("(")[1].split(")")[0],data_list) }) # calling parse_data() which returns requested data
        
            # Encoding and sending JSON string

            json_string = json.dumps(data)
            print("Sending JSON string: ",json_string)

            RPIServer.sendto(json_string,ip)
            print ("SENT to:-", ip, server_port, "From", server_ip)
            # Convert into JSON using json encoder, send to client using socket file transfer?
                    # https://stackoverflow.com/questions/42397511/python-how-to-get-json-object-from-a-udp-received-packet
            
            # Sort dictionary alphabetically by key before encoding? use:    sorted_dict = dict(sorted(unsorted_dict.items()))  KEYS CANNOT CONTAIN NUMBERS!!
            # (sorting might be best suited to ground station though)

