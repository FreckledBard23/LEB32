#           #--------------------------------------------------------------------#
#           |                                                                    |
#           |                        -- LEB32 COMPILER --                        |
#           |                                                                    |
#           |                          Official Compiler                         |
#           |                            for the LEB32                           |
#           |                                                                    |
#           |                       Created by FreckledBard23                    |
#           |                                                                    |
#           #--------------------------------------------------------------------#

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
        if full_striped != '':
            pc_line = pre_compile_line()
            pc_line.line = li.rstrip()
            pc_line.tabs = indentation(li)

            lines_in_LEB.append(pc_line)

    for i in range(len(lines_in_LEB)):
        if i != 0:
            if lines_in_LEB[i].tabs == lines_in_LEB[i - 1].tabs:
                lines_in_LEB[i].indentation_change = 0

            if lines_in_LEB[i].tabs >  lines_in_LEB[i - 1].tabs:
                difference_in_tabs = lines_in_LEB[i].tabs - lines_in_LEB[i - 1].tabs
                lines_in_LEB[i].indentation_change = 1

            if lines_in_LEB[i].tabs <  lines_in_LEB[i - 1].tabs:
                d = lines_in_LEB[i - 1].tabs - lines_in_LEB[i].tabs
                lines_in_LEB[i].indentation_change = -round(d / difference_in_tabs)


# ------------------------------------------------------------------------------------------ #
# ----------------------------------------- LEXER? ----------------------------------------- #
# ------------------------------------------------------------------------------------------ #
                

class broken_down_line:
    tokens = [''] * 0
    indentation_change = 0

lexed_lines = [broken_down_line] * 0

for line in lines_in_LEB:
    bdl = broken_down_line()
    bdl.indentation_change = line.indentation_change
    bdl.tokens = line.line.strip().split(' ')

    lexed_lines.append(bdl)


# ------------------------------------------------------------------------------------------ #
# ------------------------------------ ADDRESSING LINES ------------------------------------ #
# ------------------------------------------------------------------------------------------ #

class further_proccessed_line:
    tokens = [''] * 0
    indentation_change = 0
    instruction_len = 0
    address = 0

further_proccessed_lines = [further_proccessed_line] * 0

address = 0

for i in range(len(lexed_lines)):
    fpl = further_proccessed_line()

    fpl.tokens = lexed_lines[i].tokens
    fpl.indentation_change = lexed_lines[i].indentation_change
    fpl.address = address

    inst_len = 0

    if fpl.tokens[0] == 'if':
        inst_len = 3
    
    if fpl.tokens[0] == 'set':
        inst_len = 1

    if fpl.tokens[0] == 'result':
        inst_len = 3

    if fpl.tokens[0] == 'pixel':
        inst_len = 3

    if fpl.tokens[0] == 'push':
        inst_len = 1

    if fpl.tokens[0] == 'pop':
        inst_len = 1

    if fpl.tokens[0] == 'end':
        inst_len = 1

    fpl.instruction_len = inst_len
    address += inst_len

    further_proccessed_lines.append(fpl)

# ------------------------------------------------------------------------------------------ #
# --------------------------------  PUTTING IT ALL TOGETHER -------------------------------- #
# ------------------------------------------------------------------------------------------ #


class compiler_stack_item:
    start_address = 0
    end_address = 0

compiler_stack = [compiler_stack_item] * 0

for line in further_proccessed_lines:
    instructions = [0] * line.instruction_len