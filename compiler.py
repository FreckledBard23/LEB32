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

rom = [None] * 16777216
input_file = input("Filename In: ")

if not input_file.endswith(".leb"):
    print("You need to input a .leb file!")
    sys.exit(1)

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

for line in lines_in_LEB:
    bdl = broken_down_line()
    bdl.indentation_change = line.indentation_change
    bdl.tokens = line.line.strip().split(' ')

    for index in range(len(bdl.tokens)):
        if bdl.tokens[0] != 'undefine':
            bdl.tokens[index] = check_define_lookup(bdl.tokens[index])

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
      "goto": 1,
}

def is_convertible_to_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def find_extra_instructions(tokens):
    if tokens[0] == 'if' and is_convertible_to_int(tokens[3]):
        return 2
    if tokens[0] == 'result' and is_convertible_to_int(tokens[4]):
        return 2
    if tokens[0] == 'pixel' and is_convertible_to_int(tokens[3]):
        return 2
    if tokens[0] == 'store' and is_convertible_to_int(tokens[3]):
        return 2
    if tokens[0] == 'read' and is_convertible_to_int(tokens[2]):
        return 2
    if tokens[0] == 'while' and is_convertible_to_int(tokens[3]):
        return 2
    
    return 0

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
        extra_insts = find_extra_instructions(fpl.tokens)

        fpl.extra_insts = extra_insts
        fpl.instruction_len = inst_len + extra_insts
        address += inst_len + extra_insts

        further_proccessed_lines.append(fpl)

# ------------------------------------------------------------------------------------------ #
# -------------------------------- ADDRESSING COMPILE STACK -------------------------------- #
# ------------------------------------------------------------------------------------------ #


class complete_line:
    tokens = [''] * 0
    indentation_change = 0
    instruction_len = 0
    address = 0
    extra_insts = 0

    while_after = False
    while_address = 0
    while_tokens = [''] * 0
    while_ext_insts = 0

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

                if line.tokens[0] == 'while':
                    complete_lines[line_index + index_offset].while_tokens = line.tokens
                    complete_lines[line_index + index_offset].while_after = True
                    complete_lines[line_index + index_offset].while_address = line.address
                    complete_lines[line_index + index_offset].while_ext_insts = line.extra_insts

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

if_lookup = {
    "==": 1,
    "!=": 2,
     ">": 3,
     "<": 4,
    ">=": 5,
    "<=": 6
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

def create_instruction(inst_data, W1, R1, R2, inst):
    instruction =  inst_data << 16
    instruction += W1 << 12
    instruction += R1 << 8
    instruction += R2 << 4
    instruction += inst

    return instruction

for line in complete_lines:
    instructions = [0] * line.instruction_len