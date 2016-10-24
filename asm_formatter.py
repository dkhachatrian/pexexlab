import re

# taking in si_full.txt as input

reg_dict = {} #name of reg: reg_val
asm_cmds = [] #list of asm commands found in lines
mem_dict = {} #when things get pushed into memory, hold values here until overwritten

cur_file = ''
cur_line_no = -1
asm_loc_info = ''
asm_instr = ''
cur_reg2val = [] #to be appended to line of instruction.
# Updated per-machine instruction, and so temporary
# goes in order [reg1, val1, reg2, val2,...] for changed vals in machine instruction

mem_effect_str = '' #filled in by parse_asm_instruction

def parse_line(line):
	''' Look at each line for keywords. Act appropriately. '''

	if 'Watchpoint ' in line:
		cur_changed_reg = line.split[-1]
		cur_reg2val.append(cur_changed_reg)
		# changed_regs[line.split[-1]] = None
		# changed_regs.append(line.split[-1]) #last value in line

	if 'New value' in line:
		new_reg_val = line.split('=')[-1] #last val
		#convert to hex with leading '0x'
		new_reg_val = '0x{0:x}'.format(new_reg_val)
		cur_reg2val.append(new_reg_val)



	if 'at ' in line: #may have changed files
		cut = line.split()
		# 'at' is second-to-last word
		# name of file is to the right of 'at', proceeded by a colon
		cur_file = cut[-1].split(':')[0]

	if line.startswith('=>'): #ASM line
		asm_line = line[3:] #cut off =>
		asm_loc_info, asm_instr = asm_line.split(':')[0], asm_line.split(':')[1]

		# get asm_instr into command and args

		parse_asm_instruction(asm_line)

	if line.startswith('0x'):
		#contains source line number as value between tabs
		cur_line_no = line.split('\t')[1]
	else:
		# if valid number at front, is new line no
		try:
			cur_line_no = int(line.split[0])
		except ValueError:
			pass


def parse_asm_instruction(asm_line):
	''' Parse asm_line for instructions, and perform it. '''

	#### format instruction properly

	# opcode and arg(s) separate by space
	sp = asm_line.split(' ')
	arg0 = None
	arg1 = None

	if len(sp) == 1:
		opcode = sp[0]
	elif len(sp) == 2:
		opcode = sp[0]
		arg0 = sp[1]
	elif len(sp) == 3:
		opcode = sp[0]
		args = sp[1]
		# need to be more careful in splitting the two arguments
		# in case the left or right operand contains memory offset notation
		# let's use the number of ) as a guide
		num_c = args.count(',')
		num_p = args.count(')')
		if num_c == 0:
			# glory hallelujah things are simple
			split_c = args.split(',')
			arg0 = split_c[0]
			arg1 = split_c[1]

		elif num_p == 1:
			# popper = None
			if ',' not in args.split(')')[1]: #it's in second arg
				# popper = 0
				split_c = args.split(',')
				arg0 = split_c[0]
				split_c.pop(0) #remove first element before mixing back together
				arg1 = ','.join(split_c)
			else: #first arg
				# popper = -1
				split_c = args.split(',')
				arg1 = split_c[-1]
				split_c.pop(-1)
				arg0 = ','.join(split_c)

		elif num_p == 2: #split by ')' instead
			arg0 = args.split(')')[0] + ')'
			arg1 = args.split(')')[1] + ')'


	# now we have the command and arguments
	# let's evaluate the operands if they need to be due to parens
	args = [arg0,arg1]
	args = calculate_effective_addresses(args)

	# use data in si_full.txt to update actual values

	if arg0 is not None:
		pass


def calculate_effective_addresses(args):
	''' For each element in args, if parenthesis, convert to form
	Mn[address], where address is the address that is derferenced,
	and n is the size of the dereferenced memory address. '''

	new_args = []
	for arg in args:
		if arg is None or if '(' not in arg:
			new_args.append(arg)
			continue #no need to calculate anything
		D = 0
		R1 = 0
		R2 = 0
		S = 0
		# split, then strip away parens
		# D(R1,R2,S) = R1 + S*R2 + D
		vals = arg.split(',')
		if len(vals) <= 2: #scale isn't explicitly stated
			S = 1
		first_args = vals[0].split('(')
		if first_args[0].startswith('0x'): #there is a displacement
			D = int(first_args[0], 16) #will be hex string
		R1 = first_args[1]

		vals = [val.strip('()') for val in vals] #remove parens

		# get R2

		# perform formula

		# put result into new_args

		#  new_args.append('changed args')

	return new_args


def format_output_line(outf):
	''' Spit out line to output file. '''
	# format as denoted in Eggert's spec
	pass








# for line in file:
# 	if 'at ' in line:
