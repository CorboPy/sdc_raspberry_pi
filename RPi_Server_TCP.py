# Written by Alex Corbett, Feb 2024
# FOR OSError: [Errno 98]:
# kill -9 $(ps -A | grep python | awk '{print $1}')

### This will be the service .py file running on the on-board RPi so as long as it is turned on

## CURRENTLY WORKING ON:

# 1. Explore parallel programming. Have a message listening "parent" that will spit out "child" functions. Parent, child, and other childs would all run on different threads
# i.e. a child could be made when client specifies in the json string that they want a live feed of the tcam, the child would then run that until parent tells it to stop.
# Parent will tell it to stop when client says so in their json string (parent is constantly listening and assigning tasks to different threads) - NEED TO DO THIS PROPERLY THOUGH https://superfastpython.com/safely-stop-a-process-in-python/  
# Meanwhile, another child could be handling a command request. This allows live view from the tcam while a command or data request is being carried out (theoretically)

# 2. (maybe) Creating some kind of log file on Pi locally for testing purposes. All printed statements and error catches would be useful to append to log

# 3. "[Errno 98] Address Already In Use" sometimes pops up after shutting down server and restarting python script, this needs solving.
from datetime import datetime
import time
import socket
import json
import queue
import numpy as np
from funcs_TCP import *
import signal
from pyembedded.raspberry_pi_tools.raspberrypi import PI
pi = PI()
import os
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

## CURRENT PROBLEMS
# Need to setup TCAM stream somehow using threading or processing. Also need to establish this thread/process before main loop so can test if it exists and shut it down using something (queue? something else?) 
# TCP

#### THREAD 1
def main():
    # Setting up server. Will need to add try excepts here if anything goes wrong
    buffersize = 2048
    server_ip = pi.get_connected_ip_addr(network='wlan0').replace(" ","")
    server_port = 2222
    RPIServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # if OS error in step below, run "kill -9 $(ps -A | grep python | awk '{print $1}'" in shell
    # A proper fix might have to use .setsockopt()
    #RPIServer.setsockopt()
    RPIServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    RPIServer.bind((server_ip,server_port)) 
    print("Server is running under IP ",server_ip," and port ",server_port) 

    # Listen for incoming connections
    RPIServer.listen(1)

    data_list=["TIME","TCAM","VOLT","TEMP","IPAD","WLAN","ANGZ"] # For additional intentifiable data reqs, add them here and then add them to parse_data() in funcs_TCP.py!!!!!!
    cmmd_list=["AOCS","CMD2","CMD3"] # For additional intentifiable 4-character cmmd's, add them here and then add them to parse_cmd() in funcs.py!!!!!!
    signal.signal(signal.SIGINT, signal.SIG_DFL)    # Requred to allow CTRL/C exits for resvfrom()

    # MIGHT WANT TO ADD PASSWORD CHECK HERE TO AVOID ANY RANDO INTERFERING WITH THE PI ON COMPETITION DAY 
    result=None
    while True:
        #Initial message handling and acknowledgement
        print("In loop, waiting for a connection.")
        # Wait for a connection
        connection, client_address = RPIServer.accept()
        q1 = queue.Queue()
        t1 = threading.Thread(target=live_tcam, args=(q1,connection))    # Listening
        t1.start()
        try:
            print('Connection from', client_address,"\n")
            while True:
                data = connection.recv(buffersize)  
                try:
                    msg_str = str(data.decode('utf-8')) 
                except Exception as error:
                    print("Error in parsing received message: ",error)
                    continue #????
                try:
                    msg = json.loads(msg_str)
                except Exception as error:
                    print("JSON decode error: ",error)
                    # log file? so dont lose message?
                    if msg_str == '':
                        print("Client has disconnected.\n")
                        q1.put(False)
                        #result="DISCONNECTED"
                    break
                
                now_rec = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
                acknowl = "(Server) Message: %s received from %s at %s " % (str(msg_str), str(client_address) , str(now_rec))
                print(acknowl)
                connection.sendall(acknowl.encode("utf-8"))  #quick response to client to say server has recieved msg
                print("Acknowledgement sent to %s" % str(client_address))

                try:
                    result = parse_msg(connection,msg,data_list,t1,q1)
                except Exception as err:
                    print("Error in parsing message: ",err)
                    break

                if result == "SHUTDOWN":
                    break
            #this indent = end/after the data receive while true loop GIVEN connection established from previous loop
                
        except Exception as error:
            print("Error in connection loop: ",error)
        finally:
            # Clean up the connection - what to do if shutting down?
            if t1.is_alive():
                    q1.put("KILL")
                    t1.join()
            connection.close()
            if result == "SHUTDOWN":
                RPIServer.shutdown(socket.SHUT_RDWR)
                break
            continue


    #pi shutdown things here - INCOMPLETE, currently only ends python script

    print("Server has shutdown")

if __name__=="__main__":
    main()
