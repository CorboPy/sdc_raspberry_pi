{incomplete}

Concept: decodable messages

General:
"cmd:cmd1(),cmd2(),cmd3().data:dat1(),dat2(),dat3()"
where cmdn is an example nth command. They will not be called this, they will have a 4-character cmd or data identifier - i.e. cmd:aocs() or data:rpi_t()

Power off:
"cmd:poff" ONLY

Live TCAM:
"cmd:live" ONLY

For data req only:
"cmd:None.data:dat1()"

For cmds only:
"cmd:cmd1().data:None"
