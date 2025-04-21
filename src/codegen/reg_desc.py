from collections import defaultdict
from .register import *

class RegisterDescriptor:
	def __init__(self, reg_list: list[Register]):
		self.registers = defaultdict(list)
		self.free_regs = list()
		for reg in reg_list:
			self.registers[reg] = list()

	def get_register_values(self, register):
		return self.registers[register]
  
	def set_register_values(self, register, val):
		self.registers[register] = [val]
		if register in self.free_regs:
			self.free_regs.remove(register)
  
	def clear_register(self, register):
		self.registers[register] = list()
		if register not in self.free_regs:
			self.free_regs.add(register)
  
	def discard_from_reg(self, register, value):
		self.registers[register].discard(value)
		if not self.registers[register]:
			self.free_regs.add(register)
	
	def add_var_to_register(self, register, var):
		self.registers[register].add(var)
		if register in self.free_regs:
			self.free_regs.remove(register)

	def get_free_register(self):
		if self.free_regs:
			return self.free_regs[0]
		else:
			return None
  
#   def get_registers_having(self,value):
#     reg_set = []
#     for register, vals in self.registers.items():
#       if value in vals:
#         reg_set.append(register)
#     return reg_set
  
  