class Jack_compiler:
    def __init__(self):

        # Keeps all xml translation of .jack file.
        self.xml_codes = ['<tokens>']



        # Keywords
        self.keywords = [
                    'class' ,
                    'constructor' ,
                    'function' ,
                    'method' ,
                    'field' ,
                    'static' ,
                    'var' ,
                    'int' ,
                    'char' ,
                    'boolean' ,
                    'void' ,
                    'true' ,
                    'false' ,
                    'null' ,
                    'this' ,
                    'let' ,
                    'do' ,
                    'if' ,
                    'else' ,
                    'while' ,
                    'return'
                    ]


        # Symbols
        self.symbols = [
                    '{' ,
                    '}' ,
                    '(' ,
                    ')' ,
                    '[' ,
                    ']' ,
                    '.' ,
                    ',' ,
                    ';' ,
                    '+' ,
                    '-' ,
                    '*' ,
                    '/' ,
                    '&' ,
                    ',' ,
                    '<' ,
                    '>' ,
                    '=' ,
                    '~' ,
                    '|'
                    ]





    def check_character_containing(self, element):
        ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        for token in element:
            if token in ascii_letters:
                pass
            else:
                return False
        return True



    def select_string_from_given_line(self,elements_of_line):
        string_constant = ''
        begin_concat = 0
        stop = 1
        double_quotation_occurance_number = 0
        element_counter = 0
        for element in elements_of_line:

            if element[0] == '"':
                begin_concat = 1
                double_quotation_occurance_number += 1

            if element[-1] == '"':
                string_constant += ' ' + element
                begin_concat = 0
                double_quotation_occurance_number += 1
                elements_of_line[element_counter] =' '

            if begin_concat == 1:
                string_constant += ' ' + element
                elements_of_line[element_counter] =' '

            if double_quotation_occurance_number == 2:
                break

            element_counter += 1

        return string_constant





    def convert_line(self, pure_jack_code):

        # Go through all elements of line.
        elements_of_line = pure_jack_code.split()
        element_counter = 0

        number_of_double_quotation = pure_jack_code.count('"')
        quotation_counter = 0



        for element in elements_of_line:

            append_to_main_xml_codes = 0
            is_identifier = 1
            xml_translation_of_line = ''

            if element in self.keywords:
                xml_translation_of_line = '<keyword> ' + element.strip() + ' </keyword>'
                is_identifier = 0
                append_to_main_xml_codes = 1

            if element in self.symbols:

                if element == '<' :
                    element = '&lt;'
                if element == '>' :
                    element = '&gt;'
                if element == '&' :
                    element = '&amp;'

                xml_translation_of_line = '<symbol> ' + element.strip() + ' </symbol>'
                is_identifier = 0
                append_to_main_xml_codes = 1

            if element[0] == '"' and (number_of_double_quotation != 0) :



                """
                while elements_of_line[element_counter][-1] != '"':
                    string_constant += ' ' + elements_of_line[element_counter]
                    element_counter += 1
                    if elements_of_line[element_counter][-1] == '"':
                        string_constant += ' ' + elements_of_line[element_counter]
                """
                if (quotation_counter % 2 == 0):
                    string_constant = self.select_string_from_given_line(elements_of_line)
                    xml_translation_of_line = '<stringConstant> ' + string_constant.replace('"', '').strip() + '  </stringConstant>'
                    append_to_main_xml_codes = 1

                quotation_counter += 1
                is_identifier = 0
            if element.isdigit():
                xml_translation_of_line = '<integerConstant> ' + element.strip() + ' </integerConstant>'
                is_identifier = 0
                append_to_main_xml_codes = 1

            if is_identifier == 1:
                if (not element[0].isdigit()) and self.check_character_containing(element):
                    xml_translation_of_line = '<identifier> ' + element.strip() + ' </identifier>'
                    append_to_main_xml_codes = 1





            if append_to_main_xml_codes == 1 and element != ' ':
                self.xml_codes.append(xml_translation_of_line)

            element_counter += 1













####
