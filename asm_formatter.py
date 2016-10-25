import re

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

tabbed_digits = r'\d+\t\d+'


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

            



def parse_dump(dump, outf):
    ''' Look at each line for keywords. Act appropriately. '''

    global cur_file, cur_line_no, asm_loc_info, asm_instr, cur_reg2val, asm_instr_str

    i = 0

    for line in dump:
        i += 1 #keep track of line number for reference
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


        # vanguard line
        # process and make a new line of info (and refresh values)
        # when reaching this line
        if '+si' in line:
            mem_effects = []
            # time to execute our cleaned-up instructions!
            # i.e. say what effects on memory this has
            # let's first update our register_dict,
            # and keep track of what they changed
            for reg in cur_reg2val:
                val = cur_reg2val[reg]
                reg_dict[reg] = val
                mem_effects.append('{0}=0x{1:x}'.format(reg, val))
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
            cur_line_no = None
            asm_instr_str = ''
            # asm_line = None

            

        elif 'Watchpoint ' in line:
            cur_changed_reg = line.split()[-1]
#            cur_reg2val.append(cur_changed_reg)
            # changed_regs[line.split[-1]] = None
            # changed_regs.append(line.split[-1]) #last value in line
        elif 'New value' in line:
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



        elif 'at ' in line: #may have changed files
            cut = line.split()
            # 'at' is second-to-last word
            # name of file is to the right of 'at', proceeded by a colon
            cur_file = cut[-1].split(':')[0]

        elif line.startswith('=>'): #ASM line
            asm_line = line[3:] #cut off =>
            # asm_loc_info, asm_instr = asm_line.split(':')[0], asm_line.split(':')[1]
            asm_loc_info, asm_instr_str = asm_line.split(':')
            
            asm_instr_str = re.sub(r'\$|\t', '', asm_instr_str)
            # get asm_instr into command and args
            asm_instr = parse_asm_instruction(asm_instr_str)

        elif line.startswith('0x'):
            # contains source line number as value between tabs, if such a tab exists
            # check for two digits with tab
            if re.match(tabbed_digits, line):
                cur_line_no = line.split('\t')[1]
        else:
            # if valid number at front, is new line no
            try:
                cur_line_no = int(line.split()[0])
            except ValueError:
                pass


def update_values(asm_instr):
    ''' Given 3-element list of ASM,
    update relevant dictionaries and return
    list of string representations of changes which occurred.
    Only deals with calls into memory (not registers).'''

    # if registers were changed, already dealt with
    # so only have to deal with random memory locations being changed
    # (e.g. in the stack)

    asm_instr = [s.strip('%') for s in asm_instr if type(s) is str]

    if len(asm_instr) != 3:
        return []

    opcode, arg0, arg1 = asm_instr
    mem_effects = []
    word_size = 2 # number of bytes

    if opcode not in asm_cmds:
        return []
    if 'ret' in opcode:
        return []
    if 'pop' in opcode:
        return []
    if arg0 == '' and arg1 == '': # shouldn't be here
        return []
    # if 'ret' in opcode:


    if 'push' in opcode:
        mem_dict[reg_dict['rsp']] = arg1
        arg0 = arg1
        arg1 = reg_dict['rsp']



    if arg0 != '':
        # determine size of byte move
        temp = arg0.strip('%')
        if temp[0] == 'r':
            word_size = 8
        if temp[0] == 'e' or temp[-1] == 'd':
            word_size = 4
        if temp[-1] in ['b','h','l']:
            word_size = 1
        else: # weirder cases...
            if arg1 != '':
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
    except KeyError:
        pass
    
    try:
        arg1 = reg_aliases[arg1]
    except KeyError:
        pass

    if 'lea' not in opcode:
    # look up value for arg0 if it's a value in mem_dict or reg_dict
        try:
            arg0 = mem_dict[arg0]
        except KeyError:
            pass
        #but maybe it's a register?
        try:
            arg0 = reg_dict[arg0]
        except KeyError:
            pass
        # then it's just some number as far as we care


    
    try:
        arg1 = mem_dict[arg1]
    except KeyError:
        pass
    #but maybe it's a register?
    try:
        arg1 = reg_dict[arg1]
    except KeyError:
        pass


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
        arg0 = str2val(arg0)
    if type(arg1) is str:
        arg1 = str2val(arg1)
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
    s = 'M{0}[0x{1:x}]=0x{2:x}'.format(word_size, arg1, arg0)
    mem_effects.append(s)

    return mem_effects



def calculate_effective_addresses(args):
    ''' For each element in args, if parenthesis, convert to form
    Mn[address], where address is the address that is derferenced,
    and n is the size of the dereferenced memory address. '''

    new_args = []
    for arg in args:
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
    
    sp_s = arg_s.split(' ')
    if len(sp_s) == 2:
        arg0 = sp_s[0]
        arg1 = sp_s[1]
    
    # otherwise, can split off and know the last arg is the last
    # element in list
    else:
        sp_c = arg_s.split(',')
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
    argl = calculate_effective_addresses(argl)

    return argl


#parse_asm_instruction('movabs 0x7fffffffffffffff,%rax')

#init_reg_dict()
#parse_asm_instruction('movabs 0x7fff(%rsi,%rdi,4),%rax')


def main():

    init_reg_dict()
    init_reg_aliases()
    
    with open('si_full_io.txt') as dump:
        with open('formatted_asm.txt', 'w') as outf:
            parse_dump(dump, outf)


main()