

### This will be the service .py file running on the on-board RPi so as long as it is turned on
## Message syntax: "cmd:turn(params),command(params).data:temp(params),cam(params)". ALWAYS cmd first, ALWAYS HAVE A ". data = None" EVEN IF NOT REQUESTING DATA. 
## EXCEPTION to that rule is for "cmd: poff" which will poweroff
## "cmd" tells program client wants to perform some action on the spacecraft, "data" tells pi client wants to recieve requested data
from datetime import datetime
import time
# machine for rpi <-> r pico (requesting payload data)
# socket for network
# json for encoding


# FUNCTIONS

def aocs_control(angle,speed,etc):

    # Perform aocs control
    info = "success! (hopefully)"
    return info


def parse_cmd(cmd,params,cmd_list):
    """Returns info on cmd success/failiure

    Args:
        cmd (string): 4-character cmd identifier
        params (string): string comma list of params required for chosen cmd
        cmd_list (list): hard-coded string list of cmds
    """
    #catching in case it somehow gets through
    if cmd == "None":
        return("none")
    
    elif cmd == cmd_list[0]:  #tcam
        info = "tcam_func_recieved"
        return(info)
    elif cmd == cmd_list[1]:  #aocs
        #params
        a = float(params.split(",")[0]) # float if number, string if text, etc. Want to get it into form required by aocs_control()
        s = float(params.split(",")[1])
        e = float(params.split(",")[2])
        info = "cmd_aocs_(2)_recieved:_" + aocs_control(a,s,e)  # Might be neccesary to also return the new angle relative to something
        return(info)
    elif cmd == cmd_list[2]:  #whatever it is ...
        #perform cmd 3
        info = "cmd_3_recieved"
        return(info)
    #add additional cmds here
    else:
        info = "unidentified_cmd"
        return(info)

def parse_data(data,params,data_list):

    if data == "None":
        return("none")
    
    elif data == data_list[0]:     #Pi temp
        info = "XXXX"   #in K or deg C idk yet
        return(info)
    elif info == data_list[1]:      #Pico temp
        info = "YYYY"
        return(info)
    # add additional data reqs here
    else:
        info = "unidentified_cmd"
        return(info)


# MAIN BODY

cmd_list=["tcam","aocs","cmd3"] # For additional intentifiable commands, add them here and then add them to parse_cmd()
data_list=["pi_t","pico_t","data3"] # For additional intentifiable commands, add them here and then add them to parse_data()

while True:
    data = {}   # Dictionary later to be converted to json and sent to client

    #Getting initial message
    msg = "cmd:None.data:temp()"    #example msg

    # test if recieved a message, not sure exactly how to do this yet (this will need another indentation I think?)
    if True: # change this to sucessful message check. might be worth adding try except here too for error catching (ie poff cmd msg includes data request)
        # get current time after msg recieve success 
        now_rec = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data.update({"time_rec":now_rec})
        print(msg," recieved from (IP) at ", now_rec)
        # may also be worth creating a log file on Pi locally for testing purposes. Printed statement above would be useful to append to log

        if msg == "cmd:poff":      #THIS NEEDS TO HAPPEN FIRST I THINK - would mean cant request info if powering off        
            print("Powering off in 3,2,1...") # Maybe send this to client as well, use time to count down
            #power off rpi as everything is connected to it
            # Break? if neccessary
            # not sure on the best way to do this yet

        # Extract cmds and data requests
        cmd_reqs = msg.split(".")[0].split(":")[1].split(",")   #string list of func(params). this should work even if cmd:None only
        data_reqs = msg.split(".")[1].split(":")[1].split(",")  #string list of data(params). "..."


        # Live TCAM Request (to be implimented later down the line)
        if msg == "cmd:live":   # Might want to add this capability later down the line (this is v advanced)
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


        # Deal with commands before data
        cmd_status={}
        if cmd_reqs[0][0:3] == "None":  # first, test if None
                cmd_status.update({cmd:"none"}) 
        else:
            for cmd in cmd_reqs:
                cmd_status.update({cmd:parse_cmd(cmd[0:3],cmd.split("(")[1].split(")")[0],cmd_list)})  # calling parse_cmd() to get cmd success/failure info
        data.update({"cmd_updates":cmd_status}) # dictionary inside data dictionary specifying cmd info


        # Deal with data requests next
        for data_req in data_reqs:
            data.update({data_req:parse_data(data_req,data_req.split("(")[1].split(")")[0],data_list)}) # calling parse_data() which returns requested data
            
        # Encoding and sending JSON

        # Convert into JSON using json encoder, send to client using socket file transfer?
        # Sort dictionary alphabetically by key before encoding? use:    sorted_dict = dict(sorted(unsorted_dict.items()))  KEYS CANNOT CONTAIN NUMBERS!!
        # (sorting might be best suited to ground station though)

   