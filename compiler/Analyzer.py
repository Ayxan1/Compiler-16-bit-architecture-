from os import listdir
from os.path import isfile, join
from Tokenizer import Jack_compiler
from CompilationEngine import Compilation_Engine
from SymbolTable import symbol_table
from VMWriter import vm_writer



# File operation and some other functions.




# Pick only .jack files from given directory.
def select_jack_files(files):
    all_jack_files = []
    for file_name in files:
        start_point = file_name.index('.')
        file_type = file_name[start_point+1:]
        if file_type.strip() == 'jack':
            all_jack_files.append(file_name[:start_point])
    if all_jack_files[0] != "Main":
        index = all_jack_files.index("Main")
        temp = all_jack_files[0]
        all_jack_files[index] = temp
        all_jack_files[0] = "Main"
    return all_jack_files



# Give name to result xml file (file_name for single file or folder name for directory).
def define_xml_file_name(input):
    xml_file_name = ''
    if '\\' in input:
        start_point = input.rfind('\\')
        xml_file_name = input[start_point+1:]
    else:
        xml_file_name = input

    return xml_file_name







# This function selects pure jack codes (without any comments or spaces).
def pick_pure_jack_code(line):
    continue_flag = 0
    pure_jack_code = ''
    # For bypassing of empty lines
    if len(line.strip()) == 0 :
        continue_flag = 1

    # If line begins with comment then skip it.
    if line[0]=='/':
        continue_flag = 1


    # When there is white space between beginning of line and beginning of text in the line we ignore prespaces in the lines.  for ex:   || _ _ _ _ white space_ _ _ push constant 42
    line1 = line
    if line1[0] == ' ':
        i = find_letter_starting(line1, "bypass_white_space")
        line1 = line[i+1:]

    # Ignoring api comments.
    if (line1[0] == '/' ) or (line1[0] == '*'):
        continue_flag = 1


    # Ignoring process of white spaces and comments.
    if ( line1[0]!='/' and line1[0]!='\n' and line1[0] != '*' ) and continue_flag == 0:
        if '//' in line1:
            final_point_char = '//'
        else:
            final_point_char = '\n'

        print('\n\n')
        print('-->' + final_point_char + '<--')
        print(line1)
        print('\n\n')
        # Picking pure vm code (without white spaces or comments)
        final_point = line1.index(final_point_char)

        # If there is only comment in one line we should skip it.
        if len(line1[0:final_point].strip()) == 0:
            continue_flag = 1
        else:
            pure_jack_code = line1[0:final_point].strip()
    else:
        continue_flag = 1



    if continue_flag == 0:
        pure_jack_code_temp = list(pure_jack_code)
        result_pure_jack_code = ''
        # Inserting spaces between symbol and other tokens (for making easy to picking symbols from given line).
        counter = 0
        while counter < len(pure_jack_code_temp):
            if pure_jack_code_temp[counter] in tokenizer.symbols:
                result_pure_jack_code += ' ' + pure_jack_code_temp[counter] + ' '
            else:
                result_pure_jack_code += pure_jack_code_temp[counter]

            if pure_jack_code_temp[counter] == '\n':
                break
            else:
                counter += 1

        pure_jack_code = result_pure_jack_code

    return pure_jack_code, continue_flag









# This function finds index of starting text in given line of file.
# Function is used for two purposes firstly, for ignoring white space in line.
# Secondly, finding text starting point for determing memory_segment type in -> purpose == "bypass_white_space":
# vm_command  -> if purpose == "for_determining_memory_segment":
def find_letter_starting(line, purpose):
    # Number of occurences of white spaces.
    i=0

    # Index of second white space in line.
    index = 0

    while True:
        index += 1
        if line[index] == ' ':
            i += 1
        else:
            if purpose == "bypass_white_space":
                return i
            if purpose == "for_determining_memory_segment":
                # Stop when find second white space in line.
                if i == 2:
                    return index







# Getting name of all files in given directory.
def get_files_from_directory(input_name):
    if '\\' in input_name:
        files = [f for f in listdir(input_name) if isfile(join(input_name, f))]
        all_jack_files_names = select_jack_files(files)
        input_type = "directory"
        single_file_name=''
        return all_jack_files_names, input_type, single_file_name
    else:
        single_file_name = input_name

        # For looping only one time.
        all_jack_files_names=[single_file_name]
        input_type = "file"
        return all_jack_files_names, input_type, single_file_name


# Ressetting all variables (each file has to have own data information).
def reset_current_file_variables(compilation_engine_object):
    # Stores analyzed_xml_data and line tracking  information.
    compilation_engine_object.xml_data_of_current_file = []
    compilation_engine_object.analyzed_xml_data = []
    compilation_engine_object.line_counter = 1

    # Current processed file name.
    compilation_engine_object.file_name = ''

    # Current xml_line information.
    compilation_engine_object.value = ''
    compilation_engine_object.type = ''
    compilation_engine_object.current_xml_line = ''


    # Next xml_line information.
    compilation_engine_object.next_value = ''
    compilation_engine_object.next_type = ''

    # Next next (2 steps further) information for term parsing (LL(1) case).
    compilation_engine_object.next_next_value = ''

    # For VM translation.
    # Keeps type of currently running subroutine.
    compilation_engine_object.type_of_subroutine = ''

    # Identify labels of each while statement.
    compilation_engine_object.while_label_id = -1

    # While label id stack.
    compilation_engine_object.while_label_stack = []


    # Identify labels of each if statement.
    compilation_engine_object.if_label_id = -1

    # If label id stack.
    compilation_engine_object.if_label_stack = []


    # Kind of created subroutine.
    compilation_engine_object.kind_of_subroutine = ''

    # Name of currently executing statement.
    compilation_engine_object.executing_statement = 0

    # Keeps state of subroutine executing process.
    compilation_engine_object.subroutine_is_executing = 0

    # Keeps state of array executing process.
    compilation_engine_object.array_executing = 0





# Getting name of file or directory.
input_name = input("Please enter file name or directory:")
all_jack_files_names, input_type, single_file_name = get_files_from_directory(input_name)

tokenizer = Jack_compiler()




# Looping through all files in given directory.
for file_name in all_jack_files_names:

    # Reset xml_codes for each file.
    tokenizer.xml_codes = ['<tokens>']

    # Determining of input type (file or directory).
    if input_type == "file":
        file_name = single_file_name
        with open(single_file_name + ".jack", "r") as f:
            data = f.readlines()
    if input_type == "directory":
        with open(file_name + ".jack", "r") as f:
            data = f.readlines()



    # Going through the each line of .jack file.
    for line in data:
        pure_jack_code, continue_flag = pick_pure_jack_code(line)
        if continue_flag == 1:
            continue
        else:
            tokenizer.convert_line(pure_jack_code)



    # Determining xml file name for keeping all xml codes.
    xml_file_name = file_name

    # For being able to be read by browser
    tokenizer.xml_codes.append('</tokens>')

    # Writing xml codes to file_nameT.xml (same file name with .jack file).
    f = open(xml_file_name + "T.xml", "w")
    for line in tokenizer.xml_codes:
        f.write(line+'\n')










#__________________________________Syntax Analyzer___________________________________

all_xml_files_names = []
compilation_engine = Compilation_Engine()

# Getting names of .xml files.
for file_name in all_jack_files_names:
    all_xml_files_names.append(file_name + 'T.xml')


# Reading content of xml files.
for file_name in all_xml_files_names:

    # Reading content of individual .xml file.
    with open(file_name , "r") as f:
        xml_data = f.readlines()

    # Passing content of file to CompilationEngine class.
    compilation_engine.xml_data_of_current_file = xml_data

    # Picks file name and making file name global for whole CompilationEngine class.
    compilation_engine.pick_file_name(file_name)

    # Starting of compilation of given file with calling compile_class method.
    compilation_engine.select_next_xml_line()
    if compilation_engine.next_type == 'keyword' and compilation_engine.next_value == 'class':
        compilation_engine.CompileClass()
    else:
        print('Compilation Error: wrong keyword, must be class')

    # Picking file name from file_nameT.xml.
    xml_file_name = file_name[:(file_name.index('.')-1)]
    print(xml_file_name)

    # Writing analyzed xml codes to file_name.xml .
    f = open(xml_file_name + ".xml", "w")
    for line in compilation_engine.analyzed_xml_data:
        f.write(line+'\n')


    # Showing symbol table.
    symbol_table.display_symbol_tables('both')

    # Compiled vm codes.
    print('\n\n')
    for row in vm_writer.vm_codes:
        print(row)

    # Writing vm codes of compiled file to file_name.vm.
    f = open(xml_file_name + ".vm", "w")
    for line in vm_writer.vm_codes:
        f.write(line+'\n')

    vm_writer.vm_codes = []
    # Resetting current file variables.
    reset_current_file_variables(compilation_engine)









"""


#__________________________________Creating Symbol_Table___________________________________


print('________________________________________________________________________________________')

all_analyzed_xml_files_names = []

# Getting names of analyzed .xml files.
for file_name in all_jack_files_names:
    all_analyzed_xml_files_names.append(file_name + '.xml')


# Reading content of analyzed xml files.
for file_name in all_analyzed_xml_files_names:
    # Reading content of individual analyzed .xml file.
    with open(file_name , "r") as f:
        analyzed_xml_data = f.readlines()


    # Looping through each analyzed_xml_data of individual file.
    for row in analyzed_xml_data:
        print(row)




"""








#
