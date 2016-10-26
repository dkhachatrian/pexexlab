import re
import pdb

# taking in si_full.txt as input

reg_dict = {} #name of reg: reg_val. #no % in keys
reg_aliases = {}
asm_cmds = ['push', 'pop', 'mov', 'movabs', 'lea', 'sub', 'xor', 'and', 'sar', 'sal',\
                'shr','shl' ] #list of asm commands found in lines, that will need
                # to be processed
mem_dict = {} #when things get pushed into memory, hold values here until overwritten
# will be memory_address(int) --> value(int)
# (convert to hex only as necessary)




cur_file = ''
cur_line_no = ''
asm_loc_info = ''
asm_instr = []
asm_instr_str = ''
cur_reg2val = {} #to be appended to line of instruction.
# Updated per-machine instruction, and so temporary
# goes in order [reg1, val1, reg2, val2,...] for changed vals in machine instruction

mem_effect_str = '' #filled in by parse_asm_instruction

tabbed_digits = r'0x\d+\t\d+'


def init_reg_dict():
    global reg_dict
    with open('initial_reg_vals.txt') as inf:
        for line in inf:
            line = line.strip('\n')
            if line == '' or line.startswith('#'):
                continue
            sp = line.split()
            reg_dict[sp[0]] = int(sp[1],16)

def init_reg_aliases():
    global reg_aliases
    with open('reg_aliases.txt') as inf:
        for line in inf:
            line = line.strip('\n')
            if line == '':
                continue
            line = re.sub(r' ', '', line)
            reg, aliases = line.split('=')
            alias_l = aliases.split(',')
            for e in alias_l:
                reg_aliases[e] = reg

            


name_no_pattern = re.compile(r'\w+\.\w+:\d+')

def parse_dump(dump, outf):
    ''' Look at each line for keywords. Act appropriately. '''

    global cur_file, cur_line_no, asm_loc_info, asm_instr, cur_reg2val, asm_instr_str

    i = 0

    for line in dump:
        i += 1 #keep track of line number for reference
        
#        if i == 416:
#            pdb.set_trace()
#        
        line = line.strip('\n')
        line = re.sub(r' +', ' ', line)
        if line == '':
            continue
        # Example block for one machine instruction:
        #
        #
        # 0x0000000000542146 in Ftimes (nargs=3, args=0x7fffffffd8e0)
        # at data.c:2768
        # 2768      return arith_driver (Amult, nargs, args);
        # 1: x/i $rip
        # => 0x542146 <Ftimes+6>:    mov    $0x2,%edi
        # Watchpoint 7: $rdi
        #
        # Old value = 3
        # New value = 2
        # [...]


#        # rearguard line
#        # process and make a new line of info (and refresh values)
#        # when reaching this line
#        # i.e., this is expected to come AFTER relevant info has been filled
##        if '+si' in line:
#        if line == '1: x/i $rip':
#            mem_effects = []
#            # time to execute our cleaned-up instructions!
#            # i.e. say what effects on memory this has
#            # let's first update our register_dict,
#            # and keep track of what they changed
#            for reg in cur_reg2val:
##                reg.strip('$') #match with reg_dict and spec
#                val = cur_reg2val[reg]
#                reg_dict[reg] = val
#                mem_effects.append('{0}={1}'.format(reg, val2tc(val, is_reg=True)))
#            # if any weirder locations changed, put those in mem_dict
#            # and save in mem_effects
#            mem_effects.extend(update_values(asm_instr))
#            # update output file
#            s = '{0}{1}:{2}\t{3}\t{4}\n'.format(asm_loc_info, cur_file, cur_line_no, asm_instr_str, ' '.join(mem_effects))
#            # write_to_file
#            outf.write(s)
#            # reinitialize
#            cur_reg2val = {}
#            asm_loc_info = ''
#            # cur_file is kept the same until it has reason to believe otherwise
#            cur_line_no = ''
#            asm_instr_str = ''
#            # asm_line = None
#            continue

            

        if 'Watchpoint ' in line:
            #match with reg_dict and spec
            cur_changed_reg = (line.split()[-1]).strip('$') 
#            continue
#            cur_reg2val.append(cur_changed_reg)
            # changed_regs[line.split[-1]] = None
            # changed_regs.append(line.split[-1]) #last value in line
        if 'New value' in line:
#            val = line.split('=')[-1]
            val = line.split()[-1]
            if val.startswith('0x'):
                new_reg_val = int(val,16)
            else:
                new_reg_val = int(val)
#            new_reg_val = int(line.split('=')[-1], 16) # by formatting
            # will do at the end #convert to hex with leading '0x'
            # new_reg_val = '0x{0:x}'.format(new_reg_val)
            # cur_reg2val.append(new_reg_val)
            cur_reg2val[cur_changed_reg] = new_reg_val
#            continue

        re_list = name_no_pattern.findall(line)
        
        if len(re_list) == 1:
            cur_file, cur_line_no = re_list[0].split(':')
#            continue

#        elif 'at ' in line: #may have changed files
#            cut = line.split()
#            # 'at' is second-to-last word
#            # name of file is to the right of 'at', proceeded by a colon
#            cur_file = cut[-1].split(':')[0]

        # rip updates before things execute
        if line.startswith('=>'): #ASM line
            asm_line = line[3:] #cut off =>
            # asm_loc_info, asm_instr = asm_line.split(':')[0], asm_line.split(':')[1]
            # update rip, which is advanced
            # before the ASM instruction is executed
            reg_dict['rip'] = int(asm_line.split('<')[0].strip(),16)                


            #perform updates with updated rip
            mem_effects = []
            # time to execute our cleaned-up instructions!
            # i.e. say what effects on memory this has
            # let's first update our register_dict,
            # and keep track of what they changed
            for reg in cur_reg2val:
#                reg.strip('$') #match with reg_dict and spec
                val = cur_reg2val[reg]
                reg_dict[reg] = val
                mem_effects.append('{0}={1}'.format(reg, val2tc(val, is_reg=True)))
            # if any weirder locations changed, put those in mem_dict
            # and save in mem_effects
            mem_effects.extend(update_values(asm_instr))
            # update output file
            s = '{0}{1}:{2}\t{3}\t{4}\n'.format(asm_loc_info, cur_file, cur_line_no, asm_instr_str, ' '.join(mem_effects))
            # write_to_file
            outf.write(s)
            # reinitialize
            cur_reg2val = {}
            asm_loc_info = ''
            # cur_file is kept the same until it has reason to believe otherwise
            cur_line_no = ''
            asm_instr_str = ''
            # asm_line = None




            # parse rest of line
            
            asm_loc_info, asm_instr_str = asm_line.split(':')
#            re.sub(r' ', r'', asm_loc_info) # remove spaces
            
            asm_loc_info = re.sub(r'\s', '', asm_loc_info) #remove whitespace
            
        
            
            asm_instr_str = asm_instr_str.strip()
            # get asm_instr into command and args
            asm_instr = parse_asm_instruction(asm_instr_str)
#            continue

        if line.startswith('0x'):
            # contains source line number as value between tabs, if such a tab exists
            # check for two digits with tab
            try:
                cur_line_no = int(re.sub(r'\t', r' ', line).split(' ')[1])
            except ValueError:
                pass
#            if re.match(tabbed_digits, line):
#                cur_line_no = line.split('\t')[1]
#                continue
        if cur_line_no == '':
            # if valid number at front, is new line no
            try:
                cur_line_no = int(line.split()[0].strip())
            except ValueError:
                pass


cmds_covered = ['mov', 'lea']

char_to_size = {'q': 8, 'l': 4, 'b': 1}


def update_values(asm_instr):
    ''' Given 3-element list of ASM,
    update relevant dictionaries and return
    list of string representations of changes which occurred.
    Only deals with calls into memory (not registers).'''

    # if registers were changed, already dealt with
    # so only have to deal with random memory locations being changed
    # (e.g. in the stack)

    if len(asm_instr) != 3:
        return []

    opcode, arg0, arg1 = asm_instr
    mem_effects = []
    word_size = 2 # number of bytes
    
    if arg1 in reg_aliases:
        return [] #already covered

    stay_in = False
    for cmd in cmds_covered:
        if cmd in opcode:
            stay_in = True
    if not stay_in:
        return []
#    if opcode not in asm_cmds:
#        return []
    if 'ret' in opcode:
        return []
    if 'pop' in opcode:
        return []
    if arg0 == '' and arg1 == '': # shouldn't be here
        return []
#    if arg1 in reg_aliases:
#        #already covered in main loop
#        return []
#    # if 'ret' in opcode:


    if 'push' in opcode:
        mem_dict[reg_dict['rsp']] = arg1
        arg0 = arg1
        arg1 = reg_dict['rsp']


    word_char = opcode[-1]
    
    try:
        word_size = char_to_size[word_char]
    except KeyError:
        if type(arg0) is str and arg0 != '':
            # determine size of byte move
            temp = arg0.strip('%')
            if temp[0] == 'r':
                word_size = 8
            elif temp[0] == 'e' or temp[-1] == 'd':
                word_size = 4
            elif temp[-1] in ['b','h','l']:
                word_size = 1
            else: # weirder cases...
                if type(arg1) is str and arg1 != '':
                    temp = arg1.strip('%')
                    if temp[0] == 'r':
                        word_size = 8
                    if temp[0] == 'e' or temp[-1] == 'd':
                        word_size = 4
                    if temp[-1] in ['b','h','l']:
                        word_size = 1
                else:
                    word_size = 2

    # if 'push' in opcode:
    #     # %rsp already updated before function call
    #     try:
    #         arg0 = reg_dict[arg0]
    #         mem_dict[reg_dict['%rsp']] = arg0
    #     except KeyError: #not a register. No need to lookup
    #         mem_dict[reg_dict['%rsp']] = arg0
    #     s = 'M{2}[{0:x}]={1:x}'.format(reg_dict['%rsp'], arg0, word_size)
    #     mem_effects.append(s)

    # if 'mov' in opcode and type(arg1) is int:
    #     # %rsp already updated before function call
    #     try:
    #         arg0 = reg_dict[arg0]
    #         mem_dict[reg_dict['%rsp']] = arg0
    #     except KeyError: #not a register. No need to lookup
    #         mem_dict[reg_dict['%rsp']] = arg0
    #     s = 'M{2}[{0:x}]={1:x}'.format(reg_dict['%rsp'], arg0, word_size)
    #     mem_effects.append(s)    

    # if 'lea' in opcode:
    #     pass

    # opcode arg0, arg1
    # arg1 must *not* be a register (ie must be an int)
    # arg0 may be a register *or* an address that should be followed


    try:
        arg0 = reg_aliases[arg0]
        arg0 = reg_dict[arg0]
    except KeyError:
        pass
    
    try:
        arg1 = reg_aliases[arg1]
        arg1 = reg_dict[arg1]
    except KeyError:
        pass

    if 'lea' not in opcode:
    # look up value for arg0 if it's a value in mem_dict or reg_dict
        try:
            arg0 = mem_dict[arg0]
        except KeyError:
            pass
#        #but maybe it's a register?
#        try:
#            arg0 = reg_dict[arg0]
#        except KeyError:
#            pass
#        # then it's just some number as far as we care
#

    
    try:
        arg1 = mem_dict[arg1]
    except KeyError:
        pass
#    #but maybe it's a register?
#    try:
#        arg1 = reg_dict[arg1]
#    except KeyError:
#        pass


    # if 'mov' in opcode and 'c' not in opcode: #not dealing with conditional moves...
    #     pass


    # # will change depending on opcode
    # stored_val = None

    # arg1_val = None

    # # opcodes that require knowledge of the destination's memory address's value
    # # again, assuming arg1 is not a register (so no mult, div, etc.)
    # ops_need_d = ['add', 'sub', 'and', 'or', 'xor', 'sar', 'shr', 'sal', 'shl']

    # for op in ops_need_d:
    #     if op in opcode:

    # the only times we'll be here is
    # if we're mov'ing a value into an arbitrary location in memory:
    # - loading into a register from an arbitrary location in memory
    #   is already covered before coming here
    # - randomly moving an arbitrary memory value to another arbitrary
    #   memory value is rarely an operation a program needs to perform
    # so only really need to deal with mov, lea, push commands

    if opcode.startswith('mov') or 'lea' in opcode or 'push' in opcode:
        mem_dict[arg1] = arg0

    # convert args to int if we can
    if type(arg0) is str:
        try:
            arg0 = str2val(arg0)
        except ValueError:
            pass
    if type(arg1) is str:
        try:
            arg1 = str2val(arg1)
        except ValueError:
            pass
#        arg1 = str2val(arg1)
#    try:
#        arg0 = str2val(arg0)
#    except ValueError:
#        pass
#    try:
#        arg1 = str2val(arg1)
#    except ValueError:
#        pass
    
#    f_str = ''

    # TODO: make hex values valid, i.e., make them 2's complement
    eff = 'M{0}[0x{1:x}]={2}'.format(word_size, arg1, val2tc(arg0))
    mem_effects.append(eff)

    return mem_effects

#MMAX = 2*64 - 1
#def val2mem(x):
#    ''' Converts integer to memory address (str), prepended with '0x'. '''
#    # memory addresses calls better also be nonnegative
#    # so very simple
#    return '0x{0:x}'.format(x)


# 2's complement C-representation negative numbers may look funky in Python
# since they all have values greater than TMAX according to Python's bit rules
# but they shouldn't cause errors in val2tc
VAL_MAX = 2**64 - 1 
                    
def val2tc(x, is_reg = False):
    ''' Converts integer into C-style 2's complement representation.
    Padded to nearest multiple of 8 if negative.
    If is_reg, padded to full 64 bits.
    Returns it as string, with "0x" prepended. '''
    
#    if x < 0:
#        x = ~x + 1 #2c
#    
#    if x > TMAX: #something funky happened
#        raise Exception('Input of val2tc is\
#        too large for 64-bit architecture! Overflow')
#    
#    
        
    
    if x > VAL_MAX: #funky
        raise Exception('Input of val2tc is\
        too large for 64-bit architecture! Overflow')
    
    # simple if nonnegative
    if x >= 0:
        return '0x{0:x}'.format(x)
    
    # if negative, more complicated
    
    # Python follows a signed magnitude appraoch to representing ints
    # with a literal '-' prepended in front if the value is negative
    
    # to convert to 2's complement, perform subtraction then pad with 1's
    
    # flipping bits is a bit laborious, since ~x doesn't actually flip bits
    # in Python's signed-magnitude format (unlike C)
    # so have to make mask of 1's then XOR before adding 1
    
    xb = ('{0:b}'.format(x)).strip('-') #remove negative sign
    mask = ''
    
    if is_reg:
        mask = 64*'1'
    else:
        for i in [8,16,32,64]:
            if i >= len(xb):
                mask = i*'1'
                break
#            xb = '{0}{1}'.format((i-len(xb))*'1', xb)
#            break
    
    # bitwise xor, then add 1
    # the bitwise xor with the mask also pads the front with 1's
    # so our binary representation matches the 2's complement representation
    
    xb = (int(xb,2)^int(mask,2)) + 1
    
    return '0x{0:x}'.format(xb)
    
    
#
#    x = ~x + 1 #now no '-' at front either
#    
#    # get binary representation
#    xb = '{0:b}'.format(x)
#    
#    # pad 1's to nearest proper wordsize
#    for i in [8,16,32,64]:
#        if i > len(xb):
#            xb = '{0}{1}'.format((i-len(xb))*'1', xb)
#            break
#    
#    # convert to hex
#    # (may need to manually block out 4-bits at a time?)
#    
#    xb = int(xb,2)
#    result = '0x{0:x}'.format(xb)
#    return result
#    
#    # important 

#val2tc(-25)


def calculate_effective_addresses(args):
    ''' For each element in args, if parenthesis, convert to form
    Mn[address], where address is the address that is derferenced,
    and n is the size of the dereferenced memory address. '''

    new_args = []
    for arg in args:
        try:
            arg = str2val(arg)
            new_args.append(arg)
            continue
        except ValueError:
            pass
        if arg is None or '(' not in arg:
            new_args.append(arg)
            continue #no need to calculate anything
        D = 0
        R1 = 0
        R2 = 0
        S = 1
        # split, then strip away parens
        # D(R1,R2,S) = R1 + S*R2 + D
#        vals = arg.split(',')
        d_sp = arg.split('(')
        d = d_sp.pop(0)
        if d != '':
            D = str2val(d)
        
        rs = d_sp[-1].strip(')')
        
        c_sp = rs.split(',')
        c_sp = [s.strip('%') for s in c_sp]
        
        # dpending on number of commas, know relative meanings
        if len(c_sp) == 1: #no commas
            arg = reg_dict[c_sp[0]] + D
        elif len(c_sp) == 3:
            r1,r2,s = c_sp
            if r1 != '':
                R1 = reg_dict[r1]
            if r2 != '':
                R2 = reg_dict[r2]
            if s != '':
                S = str2val(s)
            
            arg = D + R1 + S*R2
        
        new_args.append(arg)
        

                
        
#        if len(vals) <= 2: #scale isn't explicitly stated
#            S = 1
#        first_args = vals[0].split('(')
#        # if first_args[0].startswith('0x'): #there is a displacement
#        if first_args[0] != '': #there is a displacement
#            d_str = first_args[0]
#            if d_str.startswith('0x'):
#                D = int(d_str,16)
#            else:
#                D = int(d_str)
#        R1 = first_args[1]
#
#        vals = [val.strip('()') for val in vals] #remove parens
#
#        # get R2
#        if len(vals) >= 2:
#            R2 = vals[1]
#
#        # get S if existing
#        if len(vals) == 3:
#            S = vals[2]
#
#        # perform formula
#        # D(R1,R2,S) = R1 + S*R2 + D
#        a_eff = D + R1 + S*R2
#
#
#        # put result into new_args
#        new_args.append(a_eff)
#        #  new_args.append('changed args')

    return new_args


def str2val(x):
    ''' Converts string to decimal
    based on if it's hex or decimal string. '''
    if x.startswith('0x') or x.startswith('-0x'):
        return int(x,16)
    else:
        return int(x)



def parse_asm_instruction(asm_line):
    ''' Parse asm_line for instructions.
    Will not 'print out'/perform instruction until
    we reach the end of the block of machine instruction.

    Return a list of [opcode, (arg0), (arg1)].
     '''
     
    dummy_list = ['','','']
    #### format instruction properly
    asm_line = re.sub(r' +', r' ', asm_line)
    asm_line = re.sub(r'\*', r'', asm_line)

    try:
        opcode, arg_s = asm_line.split(' ')
    except ValueError: #too many for splitting to work
        return dummy_list
    
    # separates by space if destination uses an addressing mode
    arg_s = re.sub(',(-*[\d|x]*)[(]', r' \1(', arg_s)
    arg_s = re.sub(r'[%$]', r'', arg_s)
    
    sp_s = arg_s.split(' ')
    if len(sp_s) == 2:
        arg0 = sp_s[0]
        arg1 = sp_s[1]
    
    # otherwise, can split off and know the last arg is the last
    # element in list
    else:
        sp_c = [re.sub(r'%', r'', s) for s in arg_s.split(',')]
        arg1 = sp_c.pop()
        arg0 = ','.join(sp_c)
    
    
#    if ',(' in arg_s: #then second arg is memory addressing mode
#        sp = arg_s.split(',(')
#        arg0 = sp[0]
#        arg1 = 

#
#    # remove $, tabs
##    asm_line = asm_line.strip('$')
#    
#    #make sure my split with space works as expected
#    asm_line = re.sub(r',%', ', %', asm_line)
#    asm_line = re.sub(r',[(]', ', (', asm_line)
#
#    # opcode and arg(s) separate by space
#    sp = asm_line.split(' ')
#    sp = [s.strip(',') for s in sp] #if at the beginning or end, meaningless
#    opcode = sp[0]
#    arg0 = ''
#    arg1 = ''
#
#    if len(sp) == 1:
##        opcode = sp[0]
#        pass
#    elif len(sp) == 2:
##        opcode = sp[0]
#        arg0 = sp[1]
#    elif len(sp) == 3:
##        opcode = sp[0]
#        arg0 = sp[1]
#        arg1 = sp[2]
##        args = sp[1]
#        # need to be more careful in splitting the two arguments
#        # in case the left or right operand contains memory offset notation
#        # let's use the number of ) as a guide
#        num_c = args.count(',')
#        num_p = args.count(')')
#        if num_c == 0:
#            # glory hallelujah things are simple
#            split_c = args.split(',')
#            arg0 = split_c[0]
#            arg1 = split_c[1]
#
#        elif num_p == 1:
#            # popper = None
#            if ',' not in args.split(')')[1]: #it's in second arg
#                # popper = 0
#                split_c = args.split(',')
#                arg0 = split_c[0]
#                split_c.pop(0) #remove first element before mixing back together
#                arg1 = ','.join(split_c)
#            else: #first arg
#                # popper = -1
#                split_c = args.split(',')
#                arg1 = split_c[-1]
#                split_c.pop(-1)
#                arg0 = ','.join(split_c)
#
#        elif num_p == 2: #split by ')' instead
#            arg0 = args.split(')')[0] + ')'
#            arg1 = args.split(')')[1] + ')'


    # now we have the command and arguments
    # let's evaluate the operands if they need to be due to parens
    argl = [opcode, arg0,arg1]
    argl = [re.sub(r'\s', r'', s) for s in argl]
    argl = calculate_effective_addresses(argl)

    return argl


#parse_asm_instruction('movabs 0x7fffffffffffffff,%rax')

#init_reg_dict()
#parse_asm_instruction('movabs 0x7fff(%rsi,%rdi,4),%rax')




def main():

    init_reg_dict()
    init_reg_aliases()
    
    with open('si_full_io.txt') as dump:
#    with open('test_file.txt') as dump:
        with open('formatted_asm.txt', 'w') as outf:
            parse_dump(dump, outf)


main()