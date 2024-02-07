## SERVER FUNCTIONS AND PROCESSES
# need to import numpy here?

# Single tcam request
def get_tcam():
    eight_by_eight_grid = 20*np.ones(8,8) + np.random.rand(8,8)   # Get most recent tcam image data (currenly np random, for testing purposes)
    return(eight_by_eight_grid)

# LIVE TCAM PROCESS
def live_tcam(bool,ip,socket):    
    # Create pipe to process 1 so that when p1 identifies the "end live feed" command, this process checks if this has been recieved each time round the loop. THIS WILL BE COMPLICATED!!!
    bool = True
    while (bool==True):     # While still want stream running...
        # CALL GET TCAM HERE
        # SEND JSON HERE    form is {"STREAM": [8x8 matrix]}
        
        time.sleep(0.2)
        bool = toggle_q.get()
        if bool==False:
            acknowl = "Shutting down TCAM STREAM"
            print(acknowl)
            socket.sendto(acknowl,ip)
            
    # Write shutdown code here (outside loop)
    # listen for change in live cam True/False from p1. If now msg is {"STREAM":False}, stop this process PROPERLY! Very important - don't want memory leaks https://superfastpython.com/safely-stop-a-process-in-python/  
        


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
def parse_data(dat_req,ip,socket):
    """Parses data request and returns single object (float, array, etc) containing requested data. This can then be stored in a dictionary.

    Args:
        dat_req (dict): dict of full data request in dict form {"TCAM":True,"VOLT":False,"TEMP":True}
        ip (string): ip address of client
        socket (socket): server socket
    """
    
    data_out = {"TCAM":None,"VOLT":None,"TEMP":None} #  FILL FOR ALL DATAS IN DATA REQ LIST
    
    # add current time to data_list?
    if dat_req["TCAM"] == True:
        tcam_data = get_tcam()  # get latest one-off tcam data from function
        data_out["TCAM"] = tcam_data
    if dat_req["VOLT"] == True:
        voltage_data = 5    # get latest voltage data (5 placeholder, for testing purposes)
        data_out["VOLT"] = voltage_data
    if dat_req["TEMP"] == True:
        temp_data = 25    # get latest voltage data (5 placeholder, for testing purposes)
        data_out["TEMP"] = temp_data

    # add elifs for all datas!
    # add error catching to identify unidentified hiccups / errors and print + send msg to client saying what happened!

    # After the above, SEND data_out TO CLIENT
    
    json_string = json.dumps(data_out)
    print("data_out: ", json_string)
    socket.sendto(json_string,ip)
    print("Sent to ",ip)

# JSON ENCODING INFO
# Convert into JSON using json dumps, send to client using socket.sendto(msg,ip)?
# https://stackoverflow.com/questions/42397511/python-how-to-get-json-object-from-a-udp-received-packet