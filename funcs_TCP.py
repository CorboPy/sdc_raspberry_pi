## SERVER FUNCTIONS AND PROCESSES
# need to import numpy here?

from datetime import datetime
import time
import socket
import json
import threading
from multiprocessing import Process, managers
import numpy as np
from pyembedded.raspberry_pi_tools.raspberrypi import PI
pi = PI()

# Single tcam request
def get_tcam():
    eight_by_eight_grid = 20*np.ones((8,8)) + 10*np.random.random((8,8))   # Get most recent tcam image data (currenly np random, for testing purposes)
    
    # DON'T NEED loads of decimals, truncate to save link budget:
    return(eight_by_eight_grid.round(decimals=2).tolist())

def imu_angle():
    # will need to integrate imu data from mpu6050-raspberrypi

    # Mock data:
    angz = (np.random.random()*5)-2.5+90  # Pointed around 90 deg on IMU
    return(round(angz,2))  

# LIVE TCAM PROCESS
def live_tcam(q1,connection):   
    bool=False
    while True:     #checking all the time
        if not q1.empty():
                bool = q1.get()
                print("(t1) bool: ",bool)
        while bool==True:
            matrix = get_tcam()
            angz = imu_angle()
            data_out = {"STREAM":[matrix,angz]}
            json_string = json.dumps(data_out)
            connection.sendall(json_string.encode('utf-8'))
            time.sleep(1)

            if not q1.empty():
                bool = q1.get()
                print("BOOL UPDATE: ",bool)
            if bool==False:
                acknowl = "(t1) Ending TCAM STREAM"
                print(acknowl)
                connection.sendall(acknowl.encode('utf-8'))
                break
        if bool=='KILL':
            break
    print("(t1) Shutting down.") 
        


# Commands:
# need one to power off?
def aocs_control(angle,speed,etc):

    # Perform aocs control
    info = "success! (hopefully)"
    return info

# COMMAND PROCESS - this function might be best suited as the cmd process as can check if this is running directly from P1 and tell client "sorry mate, a command is already being executed!!!" 
# The function below will be called when process 1 identifies the message as a command request. This func will then route the request to the specific command func above
def parse_cmd(cmd_dict,cmmd_list,ip,socket):  # For additional intentifiable commands, add them to cmd_list and then add an extra elif to the parse_cmd() func
    """Performs requested command and returns info on cmd success/failiure 

    Args:
        cmd_dict (string): decoded JSON string in form {"cmmd":[param1,param2,param3]} 
        cmd_list (list): hard-coded list of 4-character cmmd identifiers 
        ip (string): ip address of client
        socket (socket): server socket
    """
    # Extracting the requested cmmd and its params
    cmmd = list(cmmd.keys())[0]
    params = list(cmd_dict[cmmd])
    
    if cmmd == cmmd_list[0]:  #aocs
        print("AOCS command")
        a, b, c = params[0],params[1],params[2]
        cmmd_output = aocs_control(float(a),b,c)
        info = "cmd_aocs_(2)_received:_" + cmmd_output  # May need to turn param into float, etc
        # Might be helpful to also return the old and new angle/coordinate from IMU? Or this would confuse things? If not, it would only mean client has to ask for new data after cmd completion
        # Send cmd update to client here
        return(info)

    #add additional cmmd elifs here

    else:
        info = cmmd + " is_an_unidentified_cmd"
        # Send this to client here
        return(info)


# DATA PROCESS - P1 can check if this is running directly and tell client "sorry mate, a data request is already underway!!! Try again later..." 
# The function below will be called when process 1 identifies the message as a data request. This func will then identify all data requests from True/False in the recieved JSON
def parse_data(dat_req,connection):
    """Parses data request and returns single object (float, array, etc) containing requested data. This can then be stored in a dictionary.

    Args:
        dat_req (dict): dict of full data request in dict form {"TCAM":True,"VOLT":False,"TEMP":True}
        ip (string): ip address of client
        socket (socket): server socket
    """
    
    data_out = {"TIME":None,"TCAM":None,"VOLT":None,"TEMP":None,"IPAD":None,"WLAN":None,"ANGZ":None} #  FILL FOR ALL DATAS IN DATA REQ LIST
    

    if dat_req["TIME"] == True:
        time_data = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")  # get latest one-off tcam data from function
        data_out["TIME"] = time_data
    if dat_req["TCAM"] == True:
        tcam_data = get_tcam()  # get latest one-off tcam data from function
        data_out["TCAM"] = tcam_data
    if dat_req["VOLT"] == True:
        voltage_data = 5    # get latest voltage data (5 placeholder, for testing purposes)
        data_out["VOLT"] = voltage_data
    if dat_req["TEMP"] == True:
        temp_data = pi.get_cpu_temp()    # get latest cpu temp
        data_out["TEMP"] = temp_data
    if dat_req["IPAD"] == True:
        ipad_data = pi.get_connected_ip_addr(network='wlan0').replace(" ","")   # get PI ip address
        data_out["IPAD"] = ipad_data
    if dat_req["WLAN"] == True:
        wlan_data = pi.get_wifi_status()    # get wifi infomation
        data_out["WLAN"] = wlan_data
    if dat_req["ANGZ"] == True:
        angz_data = imu_angle()
        data_out["ANGZ"] = angz_data


    # add error catching to identify unidentified hiccups / errors and print + send msg to client saying what happened! 
        # an example being forgot to send TEMP in dictionary

    # After the above, SEND data_out TO CLIENT
    
    json_string = json.dumps(data_out)
    print("data_out: ", json_string)
    connection.sendall(json_string.encode('utf-8'))
    print("Sent to connection.")

# JSON ENCODING INFO
# Convert into JSON using json dumps, send to client using socket.sendto(msg,ip)?
# https://stackoverflow.com/questions/42397511/python-how-to-get-json-object-from-a-udp-received-packet
    
def parse_msg(connection,msg,data_list,t1,q1):

    # Message decoding
    keysList = list(msg.keys())

    # Determining request type - should they be elifs?
    if ((len(keysList)==1) and (keysList[0] == "SHUTDOWN")):    # SHUTDOWN
        # if p2.is_alive() == False:
        #     print("Error: please shutdown TCAM STREAM first")
        #     connection.sendto(bytes("Error: please shutdown TCAM STREAM first", "utf-8"),ip)
        # elif p2.is_alive() == False:
        print("Shutting down in...")
        connection.sendall(bytes("Shutting down in...", "utf-8"))
        time.sleep(1)
        print("3")
        connection.sendall(bytes("3", "utf-8"))
        time.sleep(1)
        print("2")
        connection.sendall(bytes("2", "utf-8"))
        time.sleep(1)
        print("1")
        connection.sendall(bytes("1", "utf-8"))
        time.sleep(2)
        return("SHUTDOWN")
        # else:
        #     print("Error: failed to determine TCAM STREAM is_alive()")
        #     connection.sendto(bytes("Error: failed to determine TCAM STREAM is_alive()", "utf-8"),ip)
        
        # I think this should stay on 1st process P1. Not much point writing function for this in funcs.py?

        # Wait for data and cmd processes to finish if still runing (something like for _ in range(10): if still running: sleep(10), else: shutdown. After loop, give up and just force shutdown other processes)

        # use time sleep to count down? Maybe send this countdown to client as well
        # power off rpi safely as everything is connected to it
        # Need to shutdown any other processes happening
        # not sure on the best way to do this yet
        # Break? if neccessary
    
    elif ((len(keysList) == 1) and (len(keysList[0])==4)):    # COMMAND json: {"CMMD":(param1,param2,param3)}
        print("Message identified as cmmd.")
        # This might need to be a multiprocess depending how how CPU intensive it is (or could set a particular command as a multiprocess)
        # info = parse_cmd(msg,cmmd_list,ip,connection)    # also handles unidentified cmds
        # print(info)

        # add try excepts to catch any non-command msgs

        supported = "Currently commands are not supported" # remove when implemented
        connection.sendall(supported.encode('utf-8')) # remove when implemented
        return(None)

    elif (len(keysList) == len(data_list)):    # DATA json: {"DATA":True,"DATA":False,.... for all data in data_list}
        parse_data(msg,connection)     # also handles unidentified data requests
        print("parse_data()")
        return(None)

    elif ((len(keysList)==1) and (keysList[0] == "STREAM")):    # TCAM STREAM json:{"STREAM":True/False}
        if msg["STREAM"] == True:
            q1.put(True)
            print("Starting TCAM STREAM")
        elif msg["STREAM"] == False:
            q1.put(False)
            print("Ending TCAM Stream")
        else:
            acknowl = "Unidentified STREAM command: " + msg
            print(acknowl)   
            connection.sendall(acknowl.encode("utf-8"))  # Telling client it's unidentified stream command
    else:
        acknowl = "Unidentified message: " + str(msg)
        print(acknowl)   
        connection.sendall(acknowl.encode("utf-8"))  # Telling client it's a completely unidentified message