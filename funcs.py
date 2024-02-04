## SERVER FUNCTIONS AND PROCESSES
# need to import numpy here?


# Single tcam request
def get_tcam():
    eight_by_eight_grid = np.zeros((8,8))   # Get most recent tcam image data (np.zeros placeholder, for testing purposes)
    return(eight_by_eight_grid)

# LIVE TCAM PROCESS
def live_tcam():    
    # Create pipe to process 1 so that when p1 identifies the "end live feed" command, this process checks if this has been recieved each time round the loop. THIS WILL BE COMPLICATED!!!
    for _ in range(10):
        print("live tcam")

        #listen for change in live cam True/False from p1. If now False, stop this process PROPERLY! Very important - don't want memory leaks https://superfastpython.com/safely-stop-a-process-in-python/  
        


# Commands:
# need one to power off?
def aocs_control(angle,speed,etc):

    # Perform aocs control
    info = "success! (hopefully)"
    return info

# COMMAND PROCESS - this function might be best suited as the cmd process as can check if this is running directly from P1 and tell client "sorry mate, a command is already being executed!!!" 
# The function below will be called when process 1 identifies the message as a command request. This func will then route the request to the specific command func above
def parse_cmd(cmd_dict,cmmd_list=["aocs","cmd2"]):  # For additional intentifiable commands, add them to cmd_list and then add an extra elif to the parse_cmd() func
    """Performs requested command and returns info on cmd success/failiure 

    Args:
        cmd_dict (string): decoded JSON string in form {"cmmd":[param1,param2,param3]} 
        cmd_list (list): hard-coded list of 4-character cmmd identifiers 
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
def parse_data(dat_req):
    """Parses data request and returns single object (float, array, etc) containing requested data. This can then be stored in a dictionary.

    Args:
        data (dict): dict of full data request in form {volt:True,curr:False,etc}
        params (string): string comma list of params required for chosen data request
        data_list (list): hard-coded string list of identifiable data requests
    """
    
    data_out = {"tcam":None,"volt":None,"temp":None} #  FILL FOR ALL DATAS IN DATA REQ LIST
    
    if dat_req["tcam"] == True:
        tcam_data = get_tcam()  # get latest tcam data
        data_out["tcam"] = tcam_data
    elif dat_req["volt"] == True:
        voltage_data = 5    # get latest voltage data (5 placeholder, for testing purposes)
        data_out["volt"] = voltage_data

    # add elifs for all datas!

    # After the above, SEND data_out TO CLIENT

