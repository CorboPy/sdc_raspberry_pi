{incomplete}

client side: https://github.com/CorboPy/sdc_ground_station

client messages to server in JSON string format:

For commands:
msg = {"CMMD" : [param1, param2, param3] } 
where "CMMD" is the 4-character command identifier, i.e. AOCS or something

For data, submit a JSON string as follows:
msg = {"TEMP" : True , "VOLT" : False , "CORD" : True, .... FOR ALL POSSIBLE DATA REQS}
Above example would tell server that client wants temp data and coordinate data. Of course, this assumes that no extra params are required for obtaining this data!

THERMAL CAM - this will be the hardest to pull off
For live thermal cam stream start:
msg = {"STREAM" : True}
For live thermal cam stream end:
msg = {"STREAM" : False}

To shutdown:
msg = {"SHUTDOWN":True}

Idea being that server-side message listening happens on one process, data parsing and sending happens on another, commands on another, thermal cam on another
Need to figure out how to stop/end/finish processes properly. Especially tcam as it will have to communicate with message-listening process somehow, using "pipe" or by writing to a file or something
