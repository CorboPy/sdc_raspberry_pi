{incomplete}

client messages to server in JSON string format:

For commands:
msg = {"cmmd" : [param1, param2, param3] } 
where "cmmd" is the 4-character command identifier

For data, submit a JSON string as follows:
msg = {"temp" : True , "volt" : False , "cord" : True, .... FOR ALL POSSIBLE DATA REQS}
Above example would tell server that client wants temp data and coordinate data. Of course, this assumes that no extra params are required for obtaining this data!

THERMAL CAM - this will be the hardest to pull off
For live thermal cam stream start:
msg = {"tcam" : True}
For live thermal cam stream end:
msg = {"tcam" : False}

Idea being that server-side message listening happens on one process, data parsing and sending happens on another, commands on another, thermal cam on another
Need to figure out how to stop/end/finish processes properly. Especially tcam as it will have to communicate with message-listening process somehow, using "pipe" or by writing to a file or something
