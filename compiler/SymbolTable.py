class Symbol_Table:
    def __init__(self):
        # Keeps the whole class level variable information.
        # Each row keeps variable Name, Type, Kind, #(sequence number)
        self.class_level_symbol_table = []


        # Keeps the whole subroutine level variable information.
        # Each row keeps variable Name, Type, Kind, #(sequence number)
        self.subroutine_level_symbol_table = []

        # For keeping sequential information of new declared variables which belong to same kind category.
        self.static_number = 0
        self.field_number = 0
        self.arg_number = 0
        self.var_number = 0


    # Resetting subroutine or class variable table.
    def reset_variable_table(self, table_kind):
        if table_kind == 'subroutine':
            self.subroutine_level_symbol_table = []
            self.arg_number = 0
            self.var_number = 0
            return
        if table_kind == 'class':
            self.class_level_symbol_table = []
            self.subroutine_level_symbol_table = []
            self.static_number = 0
            self.field_number = 0
            self.arg_number = 0
            self.var_number = 0
            return


    # This function return number of non-static variables of class.
    def count_non_static_vars(self):
        counter = 0
        for variable in self.class_level_symbol_table:
            if variable[2] == 'static':
                continue
            counter += 1
        return counter                 


    # Displays variable table information.
    def display_symbol_tables(self, table_kind):
        print('\n ---------------------------------------------------------')
        if table_kind == 'both':
            print('__________________________ Class ______________________')
            for individual_variable_info in self.class_level_symbol_table:
                print(individual_variable_info)
            print(' _______________________________________________________\n')
            print('__________________________ Subroutine ______________________')
            for individual_variable_info in self.subroutine_level_symbol_table:
                print(individual_variable_info)
            print('____________________________________________________________')
            return
        if table_kind == 'class':
            print('__________________________ Class ______________________')
            for individual_variable_info in self.class_level_symbol_table:
                print(individual_variable_info)
            print('____________________________________________________________')
            return

        if table_kind == 'subroutine':
            print('__________________________ Subroutine ______________________')
            for individual_variable_info in self.subroutine_level_symbol_table:
                print(individual_variable_info)
            print('____________________________________________________________')
            return
        print('---------------------------------------------------------\n')
        return



    # Checking existance of dublicate variables.
    def check_dublicate_variables(self, new_variable_name, table_kind):
        if table_kind == 'class':
            for row in self.class_level_symbol_table:
                if new_variable_name == row[0]:
                    print()
                    print(self.class_level_symbol_table)
                    print('new_variable_name' + new_variable_name)
                    print('row[0]' + row[0])
                    print('Compilation error: "' + new_variable_name + '" has already defined\n')
                    return 1

        if table_kind == 'subroutine':
            for row in self.subroutine_level_symbol_table:
                if new_variable_name == row[0]:
                    print('Compilation error: "' + new_variable_name + '" has already defined\n')
                    return 1
        return 0


    # Appending sequence number to variable information after that we append it to respective symbol table.
    # Checking wheter variable has already defined or not.
    def define_new_variable(self, name, type, kind):
        variable_information = [name, type, kind]
        if variable_information[2] == 'static':
            if self.check_dublicate_variables(variable_information[0], 'class') == 0:
                variable_information.append(str(self.static_number))
                self.class_level_symbol_table.append(variable_information)
                self.static_number += 1
                return
            else:
                return

        if variable_information[2] == 'field':
            if self.check_dublicate_variables(variable_information[0], 'class') == 0:
                variable_information.append(str(self.field_number))
                variable_information[2] = 'this'
                self.class_level_symbol_table.append(variable_information)
                self.field_number += 1
                return
            else:
                return

        if variable_information[2] == 'arg':
            if self.check_dublicate_variables(variable_information[0], 'subroutine') == 0:
                variable_information.append(str(self.arg_number))
                self.subroutine_level_symbol_table.append(variable_information)
                self.arg_number += 1
                return
            else:
                return

        if variable_information[2] == 'var':
            if self.check_dublicate_variables(variable_information[0], 'subroutine') == 0:
                variable_information.append(str(self.var_number))
                self.subroutine_level_symbol_table.append(variable_information)
                self.var_number += 1
                return
            else:
                return




    # This function find variable information from symbol_table. And return requested information.
    def give_variable_information(self, variable_name, requested_info):
        # Firstly variable_name is searched in subroutine scope.
        for defined_variable in self.subroutine_level_symbol_table:
            if defined_variable[0] == variable_name:
                if requested_info == 'class_name':
                    return defined_variable[1]
                if requested_info == 'all_info':
                    return defined_variable[1], defined_variable[2], defined_variable[3]

        # When given variable can not be found in subroutine scope, then look at class level variables.
        for defined_variable in self.class_level_symbol_table:
            if defined_variable[0] == variable_name:
                if requested_info == 'class_name':
                    return defined_variable[1]
                if requested_info == 'all_info':
                    return defined_variable[1], defined_variable[2], defined_variable[3]

        # If it can not be found in both scope then show compilation error.
        print('Compilation error: ' + variable_name + ' was not defined.')
        return 'DOESNT EXISTS'





symbol_table = Symbol_Table()
