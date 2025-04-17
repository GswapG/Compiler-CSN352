from collections import defaultdict

class RegisterDescriptor:
  def __init__(self,reg_list):
    self.registers = defaultdict(set)
    for reg in reg_list:
      self.registers[reg] = set()

  def get_register_values(self,register):
    return self.registers[register]
  
  def set_register_values(self,register,val):
    self.registers[register] = set(val)
  
  def clear_register(self,register):
    self.registers[register] = set()
  
  def discard_from_reg(self,register,value):
    self.registers[register].discard(value)
  
  def get_registers_having(self,value):
    reg_set = []
    for register, vals in self.registers.items():
      if value in vals:
        reg_set.append(register)
    return reg_set
  
  