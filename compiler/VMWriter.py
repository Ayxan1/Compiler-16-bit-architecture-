class Vm_writer:
    def __init__ (self):
        # Stores vm codes of current compiled file.
        self.vm_codes = []

    def write_push(self, segment, index):
        vm_segment = segment
        if segment == 'var':
            vm_segment = 'local'
        if segment == 'arg':
            vm_segment = 'argument'
            
        self.vm_codes.append('push ' + vm_segment + ' ' + str(index))
        return

    def write_pop(self, segment, index):
        vm_segment = segment
        if segment == 'var':
            vm_segment = 'local'
        if segment == 'arg':
            vm_segment = 'argument'
        self.vm_codes.append('pop ' + vm_segment + ' ' + str(index))
        return

    def write_arithmetic(self, command):
        self.vm_codes.append(command)
        return

    def write_label(self, label):
        self.vm_codes.append('label ' + label)
        return

    def write_goto(self, label):
        self.vm_codes.append('goto ' + label)
        return

    def write_if(self, label):
        self.vm_codes.append('if-goto ' + label)
        return

    def write_call(self, name, n_args):
        self.vm_codes.append('call ' + name + ' ' + str(n_args))
        return

    def write_function(self, name, n_locals):
        self.vm_codes.append('function ' + name + ' ' + str(n_locals))
        return

    def write_return(self):
        self.vm_codes.append('return')
        return



vm_writer = Vm_writer()
