
reg_dict = {} #name of reg: reg_val
asm_cmds = [] #list of asm commands found in lines

cur_file = ''

def parse_line(line):
	''' Look at each line for keywords. Act appropriately. '''

	if 'at ' in line: #may have changed files
		cut = line.split()
		# 'at' is second-to-last word
		# name of file is to the right of 'at', proceeded by a colon
		cur_file = cut[-1].split(':')[0]

	if line.startswith('=>'): #ASM line
		asm_line = line[3:] #cut off =>
		parse_asm_instruction(asm_line)

	if line.startswith('0x'): #contains source line number
		cut = line.split('\t')
		





# for line in file:
# 	if 'at ' in line:
