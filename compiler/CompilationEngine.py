from SymbolTable import symbol_table
from VMWriter import vm_writer

class Compilation_Engine:
    def __init__(self):
        # Stores analyzed_xml_data and line tracking  information.
        self.xml_data_of_current_file = []
        self.analyzed_xml_data = []
        self.line_counter = 1

        # Current processed file name.
        self.file_name = ''

        # Current xml_line information.
        self.value = ''
        self.type = ''
        self.current_xml_line = ''


        # Next xml_line information.
        self.next_value = ''
        self.next_type = ''

        # Next next (2 steps further) information for term parsing (LL(1) case).
        self.next_next_value = ''


        # For VM translation.
        # Keeps type of currently running subroutine.
        self.type_of_subroutine = ''

        # Identify labels of each while statement.
        self.while_label_id = -1

        # While label id stack.
        self.while_label_stack = []

        # Identify labels of each if statement.
        self.if_label_id = -1

        # If label id stack.
        self.if_label_stack = []

        # Kind of created subroutine.
        self.kind_of_subroutine = ''

        # Name of currently executing statement.
        self.executing_statement = 0

        # Keeps state of subroutine executing process.
        self.subroutine_is_executing = 0

        # Keeps state of array executing process.
        self.array_executing = 0



    # This function determine type and value of each token.
    def determine_type_value_of_statement(self, xml_line):
        xml_line_array = xml_line.split()
        value = xml_line_array[1]
        type = xml_line_array[0].replace('<', '').replace('>', '')

        # Collecting all string pieces from inside of <stringConstant> token.
        if type == 'stringConstant':
            for string_words in xml_line_array[2:-1]:
                value +=' ' + string_words

        return value, type


    # This function returns current xml line of given file, type and value of current token.
    def select_current_xml_line(self):
        current_xml_line = self.xml_data_of_current_file[self.line_counter]
        current_xml_line = current_xml_line.replace('\n', '')
        value, type = self.determine_type_value_of_statement(current_xml_line)
        self.analyzed_xml_data.append(current_xml_line)
        self.line_counter += 1
        self.value = value
        self.type = type
        self.current_xml_line = current_xml_line
        return


    # This function returns current xml line of given file, type and value of current token.
    def select_next_xml_line(self):
        current_xml_line = self.xml_data_of_current_file[self.line_counter]
        value, type = self.determine_type_value_of_statement(current_xml_line)
        self.next_value = value
        self.next_type = type
        return


    # This function returns current xml line of given file, type and value of current token.
    def select_next_next_xml_line(self):
        current_xml_line = self.xml_data_of_current_file[self.line_counter + 1]
        value, type = self.determine_type_value_of_statement(current_xml_line)
        self.next_next_value = value
        return


    # Picking file name from given input and assign it to self.file_name.
    def pick_file_name(self, file_name):
        # Picking file name from given input.
        file_name = file_name.replace('T', '')
        final_index = file_name.find('.')
        file_name = file_name[:final_index]
        self.file_name = file_name
        return

    # Translate subroutine declaration to vm_code.
    def convert_subroutine_dec_to_vm_code(self):
        # Identify number of parameter of subroutine.
        parameter_counter = 0
        for row in self.xml_data_of_current_file[self.line_counter:]:
            value, type = self.determine_type_value_of_statement(row)
            if type == 'identifier':
                parameter_counter += 1
            if value == ')':
                break
        vm_writer.write_function((self.file_name + '.'+ self.value), parameter_counter)
        return


    # Translate arithmetic commands to vm codes.
    def convert_arithmetic_to_vm_code(self, operation_symbol):
        vm_operation_code = ''
        if operation_symbol == '+':
            vm_operation_code = 'add'
        if operation_symbol == '-':
            vm_operation_code = 'sub'
        if operation_symbol == '=':
            vm_operation_code = 'eq'
        if operation_symbol == '>' or operation_symbol == '&gt;':
            vm_operation_code = 'gt'
        if operation_symbol == '<' or operation_symbol == '&lt;':
            vm_operation_code = 'lt'
        if operation_symbol == '|':
            vm_operation_code = 'or'
        if operation_symbol == '&' or operation_symbol == '&amp;':
            vm_operation_code = 'and'
        if operation_symbol == '*':
            vm_operation_code = 'call Math.multiply 2'
        if operation_symbol == '/':
            vm_operation_code = 'call Math.divide 2'
        if operation_symbol == 'neg':
            vm_operation_code = 'neg'
        if operation_symbol == 'not':
            vm_operation_code = 'not'
        vm_writer.write_arithmetic(vm_operation_code)
        return


    # This function parses tokenized data to analyzed data.
    def CompileClass(self):
        # Appending <class> token to analyzed xml data.
        print('<class>')
        self.analyzed_xml_data.append('<class>')
        self.select_current_xml_line()
        # Resetting all tables (subroutine and class) before adding class level variables.
        symbol_table.reset_variable_table('class')

        # Reading of class name.
        self.select_next_xml_line()
        if self.next_type == 'identifier' and self.next_value == self.file_name:
            self.select_current_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong class name identifier, must be same as file_name')

        # Reading of { symbol.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == '{':
            self.select_current_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be {')


        work_loop = 1
        while work_loop == 1:
            # Reading of variable declarations if they exist.
            self.select_next_xml_line()
            work_loop = 0

            if self.next_type == 'keyword' and (self.next_value == 'static' or \
               self.next_value == 'field'):
               self.CompileClassVarDec()
               self.select_next_xml_line()
               work_loop = 1

            # Reading of subroutine declarations if they exist.
            if self.next_type == 'keyword' and (self.next_value == 'constructor' or \
               self.next_value == 'function' or self.next_value == 'method'):
               self.CompileSubroutine()
               self.select_next_xml_line()
               work_loop = 1


        # Reading of } symbol.
        if self.next_type == 'symbol' and self.next_value == '}':
            self.select_current_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be }')
            return

        self.analyzed_xml_data.append('</class>')
        print('</class>')
        return




    # This function parsing variable declaration which was occured inside of class.
    def CompileClassVarDec(self):
        # Keeps kind, type, name information of new variable for assigning it to respective symbol table.
        new_variable_information = ['', '', '']

        # Appending <class> token to analyzed xml data.
        print(' <classVarDec>')
        self.analyzed_xml_data.append('<classVarDec>')
        self.select_current_xml_line()

        # Adding kind of variable to variable info array.
        new_variable_information[2] = self.value

        # Reading type of variable.
        self.select_next_xml_line()
        if (self.next_type == 'keyword' and (self.next_value == 'int' or \
            self.next_value == 'char' or self.next_value == 'boolean')) or \
            (self.next_type == 'identifier'):
            self.select_current_xml_line()

            # Adding type of variable to variable info array.
            new_variable_information[1] = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong type, must be int, boolean, char or class name')
            return

        # Reading the first variable name.
        self.select_next_xml_line()
        if self.next_type == 'identifier':
            self.select_current_xml_line()
            # Adding name of variable to variable info array.
            new_variable_information[0] = self.value
            symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
            return

        # Reading rest of variable declaration if they exist.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == ';':
            self.select_current_xml_line()
            self.analyzed_xml_data.append('</classVarDec>')
        else:
            while(self.next_value != ';'):
                if self.next_type == 'symbol' and self.next_value == ',':
                    self.select_current_xml_line()
                    self.select_next_xml_line()
                else:
                    print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be ,')
                    break

                if self.next_type == 'identifier':
                    self.select_current_xml_line()
                    # Adding name of variable to variable info array.
                    new_variable_information[0] = self.value
                    symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
                    self.select_next_xml_line()
                else:
                    print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
                    break

            # Appending of ;.
            self.select_current_xml_line()
            self.analyzed_xml_data.append('</classVarDec>')
        return







    #  Compiles a complete method, function, or constructor.
    def CompileSubroutine(self):
        name_of_subroutine = ''
        self.kind_of_subroutine = ''
        self.subroutine_is_executing = 1
        # Keeps referance of vm code line (which is placed above of Memor.alloc 1 line).
        # This is used for updating memory size of object.
        # This demand can happen if there will be some let statements in the body of constructor.
        address_of_vm_memalloc_code = 0

        # Resetting subroutine symbol table.
        symbol_table.reset_variable_table('subroutine')
        # Appending <subroutineDec> token to analyzed xml data.
        print('<subroutineDec>')
        self.analyzed_xml_data.append('<subroutineDec>')

        # Identifying kind of procedure construction.(method, constructor)
        self.select_current_xml_line()
        if self.value == 'constructor':
            self.kind_of_subroutine = 'constructor'
        if self.value == 'method':
            self.kind_of_subroutine = 'method'
            # Adding this to argument list of method.(subroutine level variabe table)
            symbol_table.define_new_variable('this', self.file_name, 'arg')



        # Reading type of subroutine.
        self.select_next_xml_line()
        if (self.next_type == 'keyword' and self.next_value == 'void') or \
           ((self.next_type == 'keyword' and (self.next_value == 'int'  or \
           self.next_value == 'char' or self.next_value == 'boolean'))  or \
           (self.next_type == 'identifier')):
            self.select_current_xml_line()
            self.type_of_subroutine = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong subroutine type')
            return


        # Reading name of subroutine.
        self.select_next_xml_line()
        if self.next_type == 'identifier':
            self.select_current_xml_line()
            name_of_subroutine = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong subroutine name')
            return


        # Reading ( symbol of subroutine.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == '(':
            self.select_current_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be (')
            return

        # Reading of parameter list of subroutine with calling compileParameterList method.
        self.select_next_xml_line()
        num_of_param = self.compileParameterList()


        # Reading ) symbol of subroutine.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == ')':
            self.select_current_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be )')
            return




        # Reading body of subroutine.
        # Appending <subroutineBody> token to analyzed xml data.
        print(' <subroutineBody>')
        self.analyzed_xml_data.append('<subroutineBody>')

        # Reading of {.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == '{':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be {')
            return


        # Reading variable declaration(if exists) with calling compileVarDec method.
        if self.next_type == 'keyword' and self.next_value == 'var':
            work_loop = 1
            while work_loop:
                self.compileVarDec()
                self.select_next_xml_line()
                if self.next_type == 'keyword' and (self.next_value == 'let' or \
                   self.next_value == 'if' or self.next_value == 'while'     or \
                   self.next_value == 'do' or self.next_value == 'return'       ):
                   work_loop = 0
        self.select_next_xml_line()



        # Writing subroutine declaration in vm (after counting local variabes).
        number_of_local_var = len(symbol_table.subroutine_level_symbol_table) - num_of_param
        # For methods (subtracting 1 is aiming for removing this in calculation process).
        if self.kind_of_subroutine == 'method':
            number_of_local_var -= 1
        vm_writer.write_function((self.file_name + '.'+ name_of_subroutine), number_of_local_var)

        # Allocating enough memory for object creation.
        if self.kind_of_subroutine == 'constructor':
            symbol_table.display_symbol_tables('subroutine')
            size = symbol_table.count_non_static_vars()
            vm_writer.write_push('constant', size)
            vm_writer.write_call('Memory.alloc', 1)
            vm_writer.write_pop('pointer', 0)

        # Pushing address of processed object to the stack.
        if self.kind_of_subroutine == 'method':
            vm_writer.write_push('argument', 0)
            vm_writer.write_pop('pointer', 0)



        # Reading of statements by calling compileStatements method.
        self.compileStatements()
        self.select_next_xml_line()


        # Reeading of }.
        if self.next_type == 'symbol' and self.next_value == '}':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be } subroutineBody')
            return

        self.analyzed_xml_data.append('</subroutineBody>')
        self.analyzed_xml_data.append('</subroutineDec>')
        self.kind_of_subroutine = ''
        self.subroutine_is_executing = 0
        self.if_label_id = -1
        self.while_label_id = -1
        return








    def compileParameterList(self):
        # Keeps number of parameter in subroutine declaration (for vm translation).
        num_of_param = 0
        # Appending <parameterList> token to analyzed xml data.
        print(' <parameterList>')
        self.analyzed_xml_data.append('<parameterList>')
        # Keeps kind, type, name information of new variable for assigning it to respective symbol table.
        new_variable_information = ['', '', '']
        # Adding kind of variable to variable info array (for parameters kind must be arg (argument)).
        new_variable_information[2] = 'arg'

        # Checking parameter list is empty or not
        if self.next_type == 'symbol' and self.next_value == ')':
            self.analyzed_xml_data.append('</parameterList>')
            return num_of_param
        else:
            # Reading type of variable name.
            if (self.next_type == 'keyword' and (self.next_value == 'int' or \
                self.next_value == 'char' or self.next_value == 'boolean')) or \
                (self.next_type == 'identifier'):
                self.select_current_xml_line()
                # Adding type of variable to variable info array.
                new_variable_information[1] = self.value
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong type, must be int, boolean, char or class name')
                return

            self.select_next_xml_line()

            # Reading first variable name.
            if self.next_type == 'identifier':
                self.select_current_xml_line()
                self.select_next_xml_line()
                # Adding name of variable to variable info array.
                new_variable_information[0] = self.value
                symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
                num_of_param += 1
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
                return


            # Reading rest of variable declaration if they exist.
            if self.next_type == 'symbol' and self.next_value == ')':
                self.analyzed_xml_data.append('</parameterList>')
            else:
                while(self.next_value != ')'):
                    if self.next_type == 'symbol' and self.next_value == ',':
                        self.select_current_xml_line()
                        self.select_next_xml_line()
                    else:
                        print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be ,')
                        break

                    if (self.next_type == 'keyword' and (self.next_value == 'int' or \
                        self.next_value == 'char' or self.next_value == 'boolean')) or \
                        (self.next_type == 'identifier'):
                        self.select_current_xml_line()
                        self.select_next_xml_line()
                        # Adding type of variable to variable info array.
                        new_variable_information[1] = self.value
                    else:
                        print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong type, must be int, boolean, char or class name')
                        break

                    if self.next_type == 'identifier':
                        self.select_current_xml_line()
                        self.select_next_xml_line()
                        # Adding name of variable to variable info array.
                        new_variable_information[0] = self.value
                        symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
                        num_of_param += 1
                    else:
                        print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
                        break

                self.analyzed_xml_data.append('</parameterList>')

        return num_of_param



    # Compiles a var declaration.
    def compileVarDec(self):
        # Appending <varDec> token to analyzed xml data.
        print('  <varDec>')
        self.analyzed_xml_data.append('<varDec>')
        # Keeps kind, type, name information of new variable for assigning it to respective symbol table.
        new_variable_information = ['', '', '']

        # Reading var keyword in variable declaration.
        if self.next_type == 'keyword' and self.next_value == 'var':
            self.select_current_xml_line()
            # Adding kind of variable to variable info array.
            new_variable_information[2] = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be var keyword in variable declaration')
            return

        self.select_next_xml_line()

        # Reading type of first variable.
        if (self.next_type == 'keyword' and (self.next_value == 'int' or \
            self.next_value == 'char' or self.next_value == 'boolean')) or \
            (self.next_type == 'identifier'):
            self.select_current_xml_line()
            # Adding type of variable to variable info array.
            new_variable_information[1] = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong type, must be int, boolean, char or class name')
            return

        # Reading the first variable name.
        self.select_next_xml_line()
        if self.next_type == 'identifier':
            self.select_current_xml_line()
            # Adding name of variable to variable info array.
            new_variable_information[0] = self.value
            symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
            return


        # Reading rest of variable declaration if they exist.
        self.select_next_xml_line()
        if self.next_type == 'symbol' and self.next_value == ';':
            self.select_current_xml_line()
            self.analyzed_xml_data.append('</varDec>')
        else:
            while(self.next_value != ';'):
                if self.next_type == 'symbol' and self.next_value == ',':
                    self.select_current_xml_line()
                    self.select_next_xml_line()
                else:
                    print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong symbol, must be ,')
                    break

                if self.next_type == 'identifier':
                    self.select_current_xml_line()
                    self.select_next_xml_line()
                    # Adding name of variable to variable info array.
                    new_variable_information[0] = self.value
                    symbol_table.define_new_variable(new_variable_information[0], new_variable_information[1], new_variable_information[2])
                else:
                    print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: wrong variable name')
                    break

            # Appending of ;.
            self.select_current_xml_line()
            self.analyzed_xml_data.append('</varDec>')
        return




    # Compiles a sequence of statements, not including the enclosing “{}”.
    def compileStatements(self):
        # Appending <statements> token to analyzed xml data.
        print('  <statements>')
        self.analyzed_xml_data.append('<statements>')

        while True:
            if self.next_type == 'keyword' and (self.next_value == 'let' or \
               self.next_value == 'if' or self.next_value == 'while'     or \
               self.next_value == 'do' or self.next_value == 'return'       ):

               if self.next_value == 'let':
                   self.compileLet()
                   self.select_next_xml_line()

               if self.next_value == 'do':
                   self.compileDo()
                   self.select_next_xml_line()

               if self.next_value == 'if':
                   self.compileIf()
                   self.select_next_xml_line()

               if self.next_value == 'return':
                   if self.type_of_subroutine == 'void':
                       vm_writer.write_push('constant', 0)

                   self.compileReturn()
                   self.select_next_xml_line()

               if self.next_value == 'while':
                   self.compileWhile()
                   self.select_next_xml_line()

            else:
                break

        self.analyzed_xml_data.append('</statements>')
        return



    #  Compiles a let statement.
    def compileLet(self):
        variable_name = ''

        # Appending <letStatement> token to analyzed xml data.
        print('   <letStatement>')
        self.analyzed_xml_data.append('<letStatement>')

        # Reading let keyword.
        if self.next_type == 'keyword' and self.next_value == 'let':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be let keyword')
            return

        # Reading variable name.
        if self.next_type == 'identifier':
            self.select_current_xml_line()
            self.select_next_xml_line()

            # If this identifier is a base address of array then push it to stack.
            if self.next_value == '[':
                self.array_executing =  1
                type, kind, index = symbol_table.give_variable_information(self.value, 'all_info')
                vm_writer.write_push(kind, index)

            variable_name = self.value
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be variable name')
            return

        # Reading expression if exists.
        if self.next_type == 'symbol' and self.next_value == '[':
            # Reading [.
            self.select_current_xml_line()
            self.select_next_xml_line()

            # Calling CompileExpression method.
            self.CompileExpression()
            self.select_next_xml_line()

            vm_writer.write_arithmetic('add')

            # Reading ].
            if self.next_type == 'symbol' and self.next_value == ']':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be ]')


        # Reading =.
        if self.next_type == 'symbol' and self.next_value == '=':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be =')


        # Reading rest of expression with calling CompileExpression method.
        self.CompileExpression()
        self.select_next_xml_line()

        if self.array_executing == 1:
            vm_writer.write_pop('temp', 0)
            vm_writer.write_pop('pointer', 1)
            vm_writer.write_push('temp', 0)
            vm_writer.write_pop('that', 0)
        else:
            # Write answer of expression to variable in vm.
            type, kind, index = symbol_table.give_variable_information(variable_name, 'all_info')
            vm_writer.write_pop(kind, index)


        # Reading ;.
        if self.next_type == 'symbol' and self.next_value == ';':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be ;')

        self.array_executing = 0
        self.analyzed_xml_data.append('</letStatement>')




    # Compiles a do statement.
    def compileDo(self):
        # Appending <doStatement> token to analyzed xml data.
        print('   <doStatement>')
        self.analyzed_xml_data.append('<doStatement>')
        self.executing_statement = 'do'

        # Reading of do keyword.
        if self.next_type == 'keyword' and self.next_value == 'do':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be do keyword')

        # Reading subroutine part of do statement.
        self.CompileSubroutineCall()
        self.select_next_xml_line()


        # Reading ;.
        if self.next_type == 'symbol' and self.next_value == ';':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used ;')

        # Ignoring returned value.
        vm_writer.write_pop('temp', 0)

        self.analyzed_xml_data.append('</doStatement>')
        self.executing_statement = ''


    # Compiles an if statement, possibly with a trailing else clause. (the module API continues on the next page).
    def compileIf(self):
        # Appending <ifStatement> token to analyzed xml data.
        self.analyzed_xml_data.append('<ifStatement>')

        # Change id for future labels and pushing this unique id to stack.
        self.if_label_id += 1
        self.if_label_stack.append(self.if_label_id)

        # Reading of if keyword.
        if self.next_type == 'keyword' and self.next_value == 'if':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be if keyword')


        # Reading of (.
        if self.next_type == 'symbol' and self.next_value == '(':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be (')
            return


        # Reading of expression by calling CompileExpression method.
        self.CompileExpression()
        self.select_next_xml_line()


        # Adding if-goto before statements for vm translation.
        vm_writer.write_if(('IF_TRUE' + str(self.if_label_stack[-1])))
        # Label for leaving if-else.
        vm_writer.write_goto(('IF_FALSE' + str(self.if_label_stack[-1])))
        # Label for else block.
        vm_writer.write_label(('IF_TRUE' + str(self.if_label_stack[-1])))

        # Reading of ).
        if self.next_type == 'symbol' and self.next_value == ')':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be )')
            return


        # Reading of {.
        if self.next_type == 'symbol' and self.next_value == '{':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be {')
            return


        # Reading of statements by calling compileStatements method.
        self.compileStatements()
        self.select_next_xml_line()



        # Reading of }.
        if self.next_type == 'symbol' and self.next_value == '}':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be }')
            return


        # Checking existance of else keyword.
        if self.next_type == 'keyword' and self.next_value == 'else':
            # Reading of else keyword.
            self.select_current_xml_line()
            self.select_next_xml_line()

            vm_writer.write_goto(('IF_END' + str(self.if_label_stack[-1])))
            vm_writer.write_label(('IF_FALSE' + str(self.if_label_stack[-1])))

            # Reading of {.
            if self.next_type == 'symbol' and self.next_value == '{':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be {')
                return




            # Reading of statements by calling compileStatements method.
            self.compileStatements()
            self.select_next_xml_line()



            vm_writer.write_label(('IF_END' + str(self.if_label_stack[-1])))

            # Reading of }.
            if self.next_type == 'symbol' and self.next_value == '}':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be }')
                return



            # Removing last id in label stack.
            self.if_label_stack.pop()

            if self.subroutine_is_executing == 0:
                self.if_label_id = -1

            self.analyzed_xml_data.append('</ifStatement>')
        else:
            vm_writer.write_label(('IF_FALSE' + str(self.if_label_stack[-1])))
            # Removing last id in label stack.
            self.if_label_stack.pop()

            if self.subroutine_is_executing == 0:
                self.if_label_id = -1

            self.analyzed_xml_data.append('</ifStatement>')








    #  Compiles a return statement.
    def compileReturn(self):
        # Appending <returnStatement> token to analyzed xml data.
        print('   <returnStatement>')
        self.analyzed_xml_data.append('<returnStatement>')

        # Reading of return keyword.
        if self.next_type == 'keyword' and self.next_value == 'return':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be return keyword')


        # Reading of expression if it exists.
        if self.next_type == 'symbol' and self.next_value == ';':
            self.select_current_xml_line()
            self.select_next_xml_line()
            self.analyzed_xml_data.append('</returnStatement>')
            vm_writer.write_return()
        else:
            self.CompileExpression()
            self.select_next_xml_line()
            vm_writer.write_return()
            if self.next_type == 'symbol' and self.next_value == ';':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used ;')

            self.analyzed_xml_data.append('</returnStatement>')



    # Compiles a while statement.
    def compileWhile(self):
        # Appending <whileStatement> token to analyzed xml data.
        print('   <whileStatement>')
        self.analyzed_xml_data.append('<whileStatement>')
        self.while_label_id += 1
        self.while_label_stack.append(self.while_label_id)

        # Reading of while keyword.
        if self.next_type == 'keyword' and self.next_value == 'while':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be while keyword')

        # Reading of (.
        if self.next_type == 'symbol' and self.next_value == '(':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used (')

        # Adding labels before expression for vm translation.
        vm_writer.write_label(('WHILE_EXP' + str(self.while_label_stack[-1])))

        # Reading of expression by calling CompileExpression method.
        self.CompileExpression()
        self.select_next_xml_line()

        # Negate result of expression (while loop translation rules).
        vm_writer.write_arithmetic('not')

        # Reading of ).
        if self.next_type == 'symbol' and self.next_value == ')':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used )')

        # Reading of {.
        if self.next_type == 'symbol' and self.next_value == '{':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used {')

        # Adding if-goto before statements for vm translation.
        vm_writer.write_if(('WHILE_END' + str(self.while_label_stack[-1])))

        # Reading of statements.
        self.compileStatements()
        self.select_next_xml_line()


        # Beginning new loop.
        vm_writer.write_goto(('WHILE_EXP' + str(self.while_label_stack[-1])))

        # Label for leaving loop.
        vm_writer.write_label(('WHILE_END' + str(self.while_label_stack[-1])))

        # Reading of }.
        if self.next_type == 'symbol' and self.next_value == '}':
            self.select_current_xml_line()
            self.select_next_xml_line()
        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used }')

        self.while_label_stack.pop()
        if self.executing_statement == 0:
            self.while_label_id = -1

        self.analyzed_xml_data.append('</whileStatement>')







    # Compiles an expression.
    def CompileExpression(self):
        # Appending <expression> token to analyzed xml data.
        print('   <expression>')
        self.analyzed_xml_data.append('<expression>')
        # Reading term with calling
        self.CompileTerm()

        # Reading rest of expression if it exists.
        if self.next_type == 'symbol' and (self.next_value == '+' or            \
                                           self.next_value == '-' or            \
                                           self.next_value == '*' or            \
                                           self.next_value == '/' or            \
                                           self.next_value == '&' or            \
                                           self.next_value == '&amp;' or        \
                                           self.next_value == '|' or            \
                                           self.next_value == '<' or            \
                                           self.next_value == '&lt;' or         \
                                           self.next_value == '>'   or          \
                                           self.next_value == '&gt;' or         \
                                           self.next_value == '='               ):

           work_loop = 1
           while work_loop == 1:
               work_loop = 0
               operation_symbol = ''
               # Reading operation symbol.
               if self.next_type == 'symbol' and (self.next_value == '+' or            \
                                                  self.next_value == '-' or            \
                                                  self.next_value == '*' or            \
                                                  self.next_value == '/' or            \
                                                  self.next_value == '&' or            \
                                                  self.next_value == '&amp;' or        \
                                                  self.next_value == '|' or            \
                                                  self.next_value == '<' or            \
                                                  self.next_value == '&lt;' or         \
                                                  self.next_value == '>'   or          \
                                                  self.next_value == '&gt;' or         \
                                                  self.next_value == '='               ):

                  self.select_current_xml_line()
                  self.select_next_xml_line()
                  work_loop = 1
                  operation_symbol = self.value
               else:
                   break


               # Checking if there is term or not.
               if (self.next_type == 'integerConstant' and (int(self.next_value) in range(0,32767))) or  \
                  (self.next_type == 'stringConstant')                        \
                  or (self.next_type == 'identifier')                                                    \
                  or (self.next_type == 'symbol' and (self.next_value == '-' or self.next_value == '~')) \
                  or (self.next_type == 'symbol' and self.next_value == '(')                             \
                  or (self.next_type == 'keyword' and (self.next_value == 'true'  or                      \
                                                   self.next_value == 'false' or                         \
                                                   self.next_value == 'null'  or                         \
                                                   self.next_value == 'this'                             \
                                                   )):
                  self.CompileTerm()
                  self.select_next_xml_line()
                  work_loop = 1
                  # Write operation in vm.
                  self.convert_arithmetic_to_vm_code(operation_symbol)
               else:
                  break


        self.analyzed_xml_data.append('</expression>')







    # Compiles a term. This routine is faced with a slight difficulty when trying to decide between some of
    # the alternative parsing rules.
    def CompileTerm(self):
        # Appending <term> token to analyzed xml data.
        print('    <term>')
        self.analyzed_xml_data.append('<term>')

        # Reading of term and initializing of next variables.
        self.select_next_xml_line()
        self.select_next_next_xml_line()

        # Reading of integer Constant if
        if (self.next_type == 'integerConstant' and (int(self.next_value) in range(0,32767)))               or  \
           (self.next_type == 'stringConstant')                                                             or  \
           (self.next_type == 'keyword' and (self.next_value == 'true'                                      or  \
                                            self.next_value == 'false'                                      or  \
                                            self.next_value == 'null'                                       or  \
                                            self.next_value == 'this'))                                     or  \
           (self.next_type == 'symbol' and (self.next_value == '-' or self.next_value == '~'))              or  \
           (self.next_type == 'identifier' and (self.next_next_value != '[' and self.next_next_value != '(' and \
                                                                                self.next_next_value != '.')):



           # Reading of unary operation term.
           if (self.next_type == 'symbol' and (self.next_value == '-' or self.next_value == '~')):
               self.select_current_xml_line()
               self.select_next_xml_line()
               front_operation = self.value
               # Reading of term.
               self.CompileTerm()
               # Writing neg and not in vm.
               if front_operation == '-':
                   vm_writer.write_arithmetic('neg')
               if front_operation == '~':
                   vm_writer.write_arithmetic('not')
               self.select_next_xml_line()
           else:
               self.select_current_xml_line()
               self.select_next_xml_line()

               # Pushing constant term value to stack.
               if self.type == 'integerConstant':
                   vm_writer.write_push('constant', self.value)

               # Pushing true term value to stack.
               if self.value == 'true':
                   vm_writer.write_push('constant', 0)
                   vm_writer.write_arithmetic('not')

               # Pushing false or null term value to stack.
               if self.value == 'false' or self.value == 'null':
                   vm_writer.write_push('constant', 0)

               if self.type == 'identifier':
                   # Write answer of expression to variable in vm.
                   type, kind, index = symbol_table.give_variable_information(self.value, 'all_info')
                   vm_writer.write_push(kind, index)

               # When term is 'this' keyword then push pointer 0.
               if self.value == 'this':
                   vm_writer.write_push('pointer', 0)


               # When term is a string constant then create string with OS string services.
               if self.type == 'stringConstant':
                   vm_writer.write_push('constant', (len(self.value)+1))
                   vm_writer.write_call('String.new', 1)
                   for letter in self.value:
                       vm_writer.write_push('constant', ord(letter))
                       vm_writer.write_call('String.appendChar', 2)

                   # Appending last space.
                   vm_writer.write_push('constant', ord(' '))
                   vm_writer.write_call('String.appendChar', 2)



           self.analyzed_xml_data.append('</term>')
           return



        # Reading of arrays (varName '[' expression ']' type terms).
        if (self.next_type == 'identifier' and self.next_next_value == '['):
            # Reading of variable name.

            self.select_current_xml_line()
            type, kind, index = symbol_table.give_variable_information(self.value, 'all_info')
            vm_writer.write_push(kind, index)
            self.select_next_xml_line()

            # Reading of [.
            if self.next_type == 'symbol' and self.next_value == '[':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be [')



            # Reading of expression.
            self.CompileExpression()
            self.select_next_xml_line()

            vm_writer.write_arithmetic('add')


            # Reading of ].
            if self.next_type == 'symbol' and self.next_value == ']':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be ]')

            vm_writer.write_pop('pointer', 1)
            vm_writer.write_push('that', 0)
            self.analyzed_xml_data.append('</term>')
            return


        # Reading of (expression) type terms.
        if self.next_type == 'symbol' and self.next_value == '(':
            # Reading of (.
            self.select_current_xml_line()
            self.select_next_xml_line()

            # Reading of expression.
            self.CompileExpression()

            # Reading of ).
            if self.next_type == 'symbol' and self.next_value == ')':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be )')

            self.analyzed_xml_data.append('</term>')
            return


        # Reading of subroutine calls.
        if (self.next_type == 'identifier' and (self.next_next_value == '(' or self.next_next_value == '.')):
            # Reading of subroutine call by calling CompileSubroutineCall method.
            self.CompileSubroutineCall()
            self.select_next_xml_line()
            self.analyzed_xml_data.append('</term>')
            return

        self.analyzed_xml_data.append('</term>')








    # This function doesn't exist in API documentation of compiler.
    # Using aim of this function is for make more simple parsing process.
    # Special token is not used for this function.
    def CompileSubroutineCall(self):
        # Keeps subroutine name for using in vm translation.
        subroutine_name = ''

        if self.next_type == 'identifier':
            self.select_current_xml_line()
            self.select_next_xml_line()
            subroutine_name = self.value

        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used subroutine name')
            return



        if self.next_type == 'symbol' and self.next_value == '(':
            self.select_current_xml_line()
            self.select_next_xml_line()

            # If calling happens inside of class method or constructor.
            if self.executing_statement == 'do':
                subroutine_name = self.file_name + '.' + subroutine_name
                vm_writer.write_push('pointer', 0)

            # Reading of expression list by calling CompileExpressionList method.
            numof_exprs = self.CompileExpressionList()
            self.select_next_xml_line()

            if self.executing_statement == 'do':
                numof_exprs += 1

            # Translating subroutine calling to vm function calling.
            vm_writer.write_call(subroutine_name, numof_exprs)

            # Reading of ).
            if self.next_type == 'symbol' and self.next_value == ')':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be )')
                return


        # If calling subroutine is method. (Compiling process of methods).
        elif self.next_type == 'symbol' and self.next_value == '.':
            self.select_current_xml_line()
            self.select_next_xml_line()
            name_of_object = subroutine_name
            class_of_processed_object = ''
            is_object_method = 0

            # If constructor or OS methods are called.
            if name_of_object[0].isupper():
                class_of_processed_object = name_of_object
            # If object.method type subroutine is called.
            if name_of_object[0].islower():
                is_object_method = 1
                class_of_processed_object = symbol_table.give_variable_information(name_of_object, 'class_name')


            # Reading of subroutine name.
            if self.next_type == 'identifier':
                self.select_current_xml_line()
                self.select_next_xml_line()
                subroutine_name = class_of_processed_object + '.' + self.value
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used subroutine name')
                return


            # Reading of (.
            if self.next_type == 'symbol' and self.next_value == '(':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be (')
                return

            # If caller is object.method() then push object base address in beforehand.
            if name_of_object[0].islower():
                type, kind, index = symbol_table.give_variable_information(name_of_object, 'all_info')
                vm_writer.write_push(kind, index)

            # Reading of expression list by calling CompileExpressionList method.
            numof_exprs = self.CompileExpressionList()
            self.select_next_xml_line()


            if is_object_method == 1:
                numof_exprs += 1

            # Translating subroutine calling to vm function calling.
            vm_writer.write_call(subroutine_name, numof_exprs)

            is_object_method = 0
            # Reading of ).
            if self.next_type == 'symbol' and self.next_value == ')':
                self.select_current_xml_line()
                self.select_next_xml_line()
            else:
                print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be )')
                return

        else:
            print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used ( or .')
            return





    # Compiles a (possibly empty) commaseparated list of expressions.
    def CompileExpressionList(self):
        # Number of expression.
        numof_exprs = 0
        # Appending <expressionList> token to analyzed xml data.
        print('     <expressionList>')
        self.analyzed_xml_data.append('<expressionList>')

        # Checking existance of expression in expression list.
        if self.next_type == 'symbol' and self.next_value == ')':
            self.analyzed_xml_data.append('</expressionList>')
            return numof_exprs
        else:
            # Reading first expression.
            self.CompileExpression()
            self.select_next_xml_line()
            numof_exprs += 1
            # Reading rest of expression if they exists.
            if self.next_type == 'symbol' and self.next_value == ')':
                self.analyzed_xml_data.append('</expressionList>')
                return numof_exprs
            else:
                while self.next_value != ')':
                    if self.next_type == 'symbol' and self.next_value == ',':
                        self.select_current_xml_line()
                        self.select_next_xml_line()
                    else:
                        print('ERROR position ->' +str(self.line_counter) + ' : ' + 'Compilation Error: must be used ,')
                        break

                    # Reading expression.
                    self.CompileExpression()
                    self.select_next_xml_line()
                    numof_exprs += 1
                self.analyzed_xml_data.append('</expressionList>')
                return numof_exprs















#
