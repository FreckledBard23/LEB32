#           #--------------------------------------------------------------------#           #
#           |                                                                    |           #
#           |                        -- LEB32 COMPILER --                        |           #
#           |                                                                    |           #
#           |                          Official Compiler                         |           #
#           |                            for the LEB32                           |           #
#           |                                                                    |           #
#           |                       Created by FreckledBard23                    |           #
#           |                                                                    |           #
#           #--------------------------------------------------------------------#           #

import sys

rom = [0] * 0
input_file = input("Filename In: ")
output_file = input("Filename Out: ")

# get file
if not input_file.endswith(".leb"):
    print("You need to input a .leb file!")
    sys.exit(1)

print("Compiling...")

# ------------------------------------------------------------------------------------------ #
# --------------------------------------- PRECOMPILE --------------------------------------- #
# ------------------------------------------------------------------------------------------ #
    

def indentation(string):
    spaces = 0
    for char in string:
        if char == ' ' or char == '\t':
            spaces = spaces + 1
        else:
            return spaces

    return spaces

class pre_compile_line:
    line = ''
    tabs = 0
    indentation_change = 0

lines_in_LEB = 0 * [pre_compile_line]

difference_in_tabs = 4

# Open input file
with open(input_file, 'r') as file:
    # Read all lines from the file into a list
    for li in file.readlines():
        full_striped = li.strip()
        if full_striped != '' and not full_striped.startswith('//'):
            pc_line = pre_compile_line()
            pc_line.line = li.rstrip()
            pc_line.tabs = indentation(li)

            lines_in_LEB.append(pc_line)

    for i in range(len(lines_in_LEB)):
        if i != 0:
            if lines_in_LEB[i].tabs == lines_in_LEB[i - 1].tabs:
                lines_in_LEB[i - 1].indentation_change = 0

            if lines_in_LEB[i].tabs >  lines_in_LEB[i - 1].tabs:
                difference_in_tabs = lines_in_LEB[i].tabs - lines_in_LEB[i - 1].tabs
                lines_in_LEB[i - 1].indentation_change = 1

            if lines_in_LEB[i].tabs <  lines_in_LEB[i - 1].tabs:
                d = lines_in_LEB[i - 1].tabs - lines_in_LEB[i].tabs
                lines_in_LEB[i - 1].indentation_change = -round(d / difference_in_tabs)


# ------------------------------------------------------------------------------------------ #
# ----------------------------------------- LEXER? ----------------------------------------- #
# ------------------------------------------------------------------------------------------ #


class define_lookup_element:
    name = ""
    value = ""

define_lookup = [define_lookup_element] * 0

def check_define_lookup(str):
    for define in define_lookup:
        if str == define.name:
            return define.value
        
    return str

class broken_down_line:
    tokens = [''] * 0
    indentation_change = 0

lexed_lines = [broken_down_line] * 0

line_index = 0
for line in lines_in_LEB:
    bdl = broken_down_line()
    bdl.indentation_change = line.indentation_change
    bdl.tokens = line.line.strip().split(' ')

    for index in range(len(bdl.tokens)):
        if bdl.tokens[0] != 'undefine':
            bdl.tokens[index] = check_define_lookup(bdl.tokens[index])

    if bdl.tokens[0] == 'while':
        loop = True
        line_index_offset = 0
        indentation_ = 0
        while loop:
            index_ = line_index + line_index_offset
            indentation_ += lines_in_LEB[max(index_ - 1, 0)].indentation_change
            if lines_in_LEB[index_].line.strip() == 'repeat' and indentation_ <= 0:
                loop = False
                lines_in_LEB[index_].line = "end" + lines_in_LEB[line_index].line.strip()

            line_index_offset += 1

    if bdl.tokens[0] == 'define':
        dle = define_lookup_element()
        dle.name = bdl.tokens[1]
        dle.value = bdl.tokens[3]
        define_lookup.append(dle)
    elif bdl.tokens[0] == 'undefine':
        for undef_index in range(len(define_lookup)):
            if define_lookup[undef_index].name == bdl.tokens[1]:
                define_lookup.pop(undef_index)
                break
    else:
        lexed_lines.append(bdl)

    line_index += 1

address = 0

# ------------------------------------------------------------------------------------------ #
# ------------------------------------ ADDRESSING LINES ------------------------------------ #
# ------------------------------------------------------------------------------------------ #

class goto_lookup_element:
    name = ""
    address = ""

goto_lookup = [goto_lookup_element] * 0

class further_proccessed_line:
    tokens = [''] * 0
    indentation_change = 0
    instruction_len = 0
    address = 0

    extra_insts = 0

further_proccessed_lines = [further_proccessed_line] * 0

base_inst_len_lookup = {
        "if": 3,
       "set": 2,
    "result": 1,
     "pixel": 1,
      "push": 1,
       "pop": 1,
       "end": 1,
     "store": 1,
      "read": 1,
     "while": 3,
                "endwhile": 3,
      "goto": 3,
}

base_cons_lookup = {
        "if": 1,
       "set": 1,
    "result": 0,
     "pixel": 0,
      "push": 0,
       "pop": 0,
       "end": 0,
     "store": 0,
      "read": 0,
     "while": 1,
                "endwhile": 1,
      "goto": 1,
}

def is_convertible_to_int(s):
    try:
        int(s, 0)
        return True
    except ValueError:
        return False

def find_extra_instructions(tokens):
    if tokens[0] == 'if' and is_convertible_to_int(tokens[3]):
        return 2, 1
    if tokens[0] == 'result' and is_convertible_to_int(tokens[4]):
        return 2, 1
    if tokens[0] == 'pixel' and is_convertible_to_int(tokens[3]):
        return 2, 1
    if tokens[0] == 'store' and is_convertible_to_int(tokens[3]):
        return 2, 1
    if tokens[0] == 'read' and is_convertible_to_int(tokens[2]):
        return 2, 1
    if (tokens[0] == 'while' or tokens[0] == 'endwhile') and is_convertible_to_int(tokens[3]):
        return 2, 1
    
    return 0, 0

const_lookup_size = 0

for i in range(len(lexed_lines)):
    fpl = further_proccessed_line()

    fpl.tokens = lexed_lines[i].tokens
    fpl.indentation_change = lexed_lines[i].indentation_change
    fpl.address = address

    if fpl.tokens[0].startswith(':') and fpl.tokens[0].endswith(':'):
        goto_token = fpl.tokens[0]
        gle = goto_lookup_element()
        gle.name = goto_token[1:-1]
        gle.address = address
        goto_lookup.append(gle)
    else:
        inst_len = base_inst_len_lookup[fpl.tokens[0]]
        const = base_cons_lookup[fpl.tokens[0]]
        extra_insts, extra_const = find_extra_instructions(fpl.tokens)

        const_lookup_size += const + extra_const

        fpl.extra_insts = extra_insts
        fpl.instruction_len = inst_len + extra_insts
        address += inst_len + extra_insts

        further_proccessed_lines.append(fpl)

for line in further_proccessed_lines:
    line.address += const_lookup_size + 2 #2 is there to ensure that the jump at start is taken into account

for gt in goto_lookup:
    gt.address += const_lookup_size + 2 #2 is there to ensure that the jump at start is taken into account

# ------------------------------------------------------------------------------------------ #
# -------------------------------- ADDRESSING COMPILE STACK -------------------------------- #
# ------------------------------------------------------------------------------------------ #


class complete_line:
    tokens = [''] * 0
    indentation_change = 0
    instruction_len = 0
    address = 0
    extra_insts = 0

    start_address = 0
    end_address = 0

complete_lines = [complete_line] * 0

for line in further_proccessed_lines:
    li = complete_line()
    li.tokens = line.tokens
    li.indentation_change = line.indentation_change
    li.instruction_len = line.instruction_len
    li.address = line.address
    li.extra_insts = line.extra_insts

    complete_lines.append(li)


class compiler_stack_item:
    start_address = 0
    end_address = 0

compiler_stack = [compiler_stack_item] * 0

end_of_while_lines = [0] * 0

line_index = 0
for line in complete_lines:
    if line.indentation_change == 1:
        csi = compiler_stack_item
        csi.start_address = line.address

        #find end address
        end_found = False
        index_offset = 0
        overall_indentation_change = 0
        while end_found == False:
            overall_indentation_change += complete_lines[line_index + index_offset].indentation_change
            if overall_indentation_change <= 0:
                csi.end_address = complete_lines[line_index + index_offset].address

                line.start_address = csi.start_address
                line.end_address = csi.end_address

                if complete_lines[line_index + index_offset + 1].tokens[0] == 'endwhile' and line.tokens[0] == 'while':
                    total_inst_len = complete_lines[line_index].instruction_len
                    complete_lines[line_index + index_offset + 1].start_address = complete_lines[line_index].address + total_inst_len

                end_found = True

            index_offset += 1

        compiler_stack.append(csi)

    if line.indentation_change < 0:
        change = line.indentation_change

        while change < 0:
            if len(compiler_stack) > 0:
                compiler_stack.pop()

            change += 1

    line_index += 1


# ------------------------------------------------------------------------------------------ #
# --------------------------------------- FINAL STEPS -------------------------------------- #
# ------------------------------------------------------------------------------------------ #

def line_index_by_addr(addr):
    for i in range(len(complete_lines)):
        if complete_lines[i].address == addr:
            return i

if_lookup = {
    "==": 1,
    "!=": 2,
     ">": 3,
     "<": 4,
    ">=": 5,
    "<=": 6
}

inverse_if_lookup = {
    "==": 2,
    "!=": 1,
     ">": 6,
     "<": 5,
    ">=": 4,
    "<=": 3
}

regs_lookup = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4, 
    'f': 5,
    'g': 6,
    'h': 7,
    'i': 8,
    'j': 9,
    'k': 10,
    'l': 11,
    'm': 12,
    'n': 13,
    'o': 14,
    'p': 15
}

alu_lookup = {
    '+': 0,
    '-': 1,
    '*': 2,
    '/': 3,
    '<<': 4,
    '>>': 5
}

def create_inst(inst_data, W1, R1, R2, inst):
    instruction =  inst_data << 16
    instruction += W1 << 12
    instruction += R1 << 8
    instruction += R2 << 4
    instruction += inst

    return instruction

def format_hex(num):
    return "{:08x}".format(num & 0xFFFFFFFF)

def format_addr(num):
    return "{:06x}".format(num)

all_instructions = [''] * 0

constant_value_lookup = [0] * 0 # section of rom at start to store all the constant values

def constant_value_mst(value, data_reg):
    constant_value_lookup.append(format_hex(value))

    if len(constant_value_lookup) > 0xFFFE:
        print("Too many constant values! (How did you pull that off?)")
        sys.exit(1)

    instructions.append(format_hex(create_inst(len(constant_value_lookup) + 1, regs_lookup['n'], 0, 0, 2)))
    instructions.append(format_hex(create_inst(0, regs_lookup[data_reg], 0, regs_lookup['n'], 3)))

def check_goto_lookup(s):
    for gte in goto_lookup:
        if gte.name == s:
            return gte.address
        
    print(f"Invalid goto tag. Given tag: {s}")
    sys.exit(1)

for line in complete_lines:
    instructions = [''] * 0

    if line.extra_insts != 0:
        if line.tokens[0] == 'if':
            constant_value_mst(int(line.tokens[3], 0), 'p')
        if line.tokens[0] == 'result':
            constant_value_mst(int(line.tokens[4], 0), 'p')
        if line.tokens[0] == 'pixel':
            constant_value_mst(int(line.tokens[3], 0), 'p')
        if line.tokens[0] == 'store':
            if int(line.tokens[3], 0) < 0x01000000:
                print(f"Store command stores to ROM (an invalid location)!\nStore command: {line.tokens}")
                sys.exit(1)
            constant_value_mst(int(line.tokens[3], 0), 'p')
        if line.tokens[0] == 'read':
            constant_value_mst(int(line.tokens[2], 0), 'p')
        if line.tokens[0] == 'while':
            constant_value_mst(int(line.tokens[3], 0), 'p')
        if line.tokens[0] == 'endwhile':
            constant_value_mst(int(line.tokens[3], 0), 'p')


    if line.tokens[0] == 'if':
        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[3]]

        data =  inverse_if_lookup[line.tokens[2]]
        data += regs_lookup['o'] << 4

        constant_value_mst(line.end_address + complete_lines[line_index_by_addr(line.end_address)].instruction_len, 'o')
        instructions.append(format_hex(create_inst(data, 0, regs_lookup[line.tokens[1]], r2, 5)))

    if line.tokens[0] == 'set':
        constant_value_mst(int(line.tokens[3], 0), line.tokens[1])

    if line.tokens[0] == 'result':
        w1 = regs_lookup[line.tokens[6]]
        r1 = regs_lookup[line.tokens[2]]

        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[4]]

        instructions.append(format_hex(create_inst(alu_lookup[line.tokens[3]], w1, r1, r2, 4)))

    if line.tokens[0] == 'pixel':
        if line.extra_insts != 0:
            r1 = regs_lookup['p']
        else:
            r1 = regs_lookup[line.tokens[3]]

        instructions.append(format_hex(create_inst(2, 0, r1, regs_lookup[line.tokens[1]], 6)))

    if line.tokens[0] == 'push':
        instructions.append(format_hex(create_inst(0, 0, regs_lookup[line.tokens[1]], 0, 7)))

    if line.tokens[0] == 'pop':
        instructions.append(format_hex(create_inst(0, regs_lookup[line.tokens[1]], 0, 0, 8)))

    if line.tokens[0] == 'end':
        instructions.append(format_hex(1))

    if line.tokens[0] == 'store':
        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[3]]

        instructions.append(format_hex(create_inst(0, 0, regs_lookup[line.tokens[1]], r2, 6)))

    if line.tokens[0] == 'read':
        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[2]]

        instructions.append(format_hex(create_inst(0, regs_lookup[line.tokens[4]], 0, r2, 3)))

    if line.tokens[0] == 'while':
        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[3]]

        data =  inverse_if_lookup[line.tokens[2]]
        data += regs_lookup['o'] << 4

        constant_value_mst(line.end_address + complete_lines[line_index_by_addr(line.end_address)].instruction_len, 'o')
        instructions.append(format_hex(create_inst(data, 0, regs_lookup[line.tokens[1]], r2, 5)))

    if line.tokens[0] == 'endwhile':
        if line.extra_insts != 0:
            r2 = regs_lookup['p']
        else:
            r2 = regs_lookup[line.tokens[3]]

        data =  if_lookup[line.tokens[2]]
        data += regs_lookup['o'] << 4

        constant_value_mst(line.start_address, 'o')
        instructions.append(format_hex(create_inst(data, 0, regs_lookup[line.tokens[1]], r2, 5)))

    if line.tokens[0] == 'goto':
        constant_value_mst(check_goto_lookup(line.tokens[1]), 'o')
        instructions.append(format_hex(create_inst(regs_lookup['o'] << 4, 0, 0, 0, 5)))

    all_instructions = all_instructions + instructions
    print(f"{format_addr(line.address)} {instructions} {line.tokens[0]}")
print(constant_value_lookup)
rom.append(format_hex(create_inst(2 + len(constant_value_lookup), regs_lookup['n'], 0, 0, 2)))
rom.append(format_hex(create_inst((regs_lookup['n'] << 4), 0, 0, 0, 5)))

rom += constant_value_lookup
rom += all_instructions

print("Done Compiling!\nStoring as file...")

while len(rom) < 0xFFFFFF + 1:
    rom.append(format_hex(0))

with open(output_file, 'w') as file:
    for i in range(0, 0xFFFFFF + 1, 8):
        file.write(f"{format_addr(i)}: {rom[i]} {rom[i + 1]} {rom[i + 2]} {rom[i + 3]} {rom[i + 4]} {rom[i + 5]} {rom[i + 6]} {rom[i + 7]}\n")

print("Done Storing!")