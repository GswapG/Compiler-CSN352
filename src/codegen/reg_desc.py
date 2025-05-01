from collections import defaultdict
from .register import *

class RegisterDescriptor:
	def __init__(self, reg_list: list[Register]):
		self.registers = defaultdict(list)
		self.free_regs = reg_list
		for reg in reg_list:
			self.registers[reg] = list()

	def get_register_values(self, register):
		"""
		Gets the values stored in a register.
		"""
		return self.registers[register].copy()
	
	def set_register_values(self, register, val):
		"""
		Sets the value of a register to a new value. removes all others
		"""
		self.registers[register] = [val]
		if register in self.free_regs:
			self.free_regs.remove(register)
  
	def clear_register(self, register):
		"""
		Clears the register and adds it to the free registers list.
		"""
		self.registers[register] = list()
		if register not in self.free_regs:
			self.free_regs.append(register)
  
	def discard_from_reg(self, register, value):
		"""
		Removes a value from the register. If the register is empty, adds it to the free registers list.
		"""
		self.registers[register].remove(value)
		if not self.registers[register]:
			self.free_regs.append(register)
	
	def add_var_to_register(self, register, var):
		"""
		Adds a variable to the register without removing the others.
		"""
		self.registers[register].append(var)
		if register in self.free_regs:
			self.free_regs.remove(register)

	def get_free_register(self):
		"""
		Returns a free register if available, otherwise returns None.
		"""
		if self.free_regs:
			return self.free_regs.pop()
		else:
			return None
  
	def __str__(self):
		"""
		Returns a string representation of the RegisterDescriptor's state.
		"""
		result = "=====Register Descriptor State:\n"
		for register, values in self.registers.items():
			reg_values = ', '.join(str(value) for value in values) if values else "None"
			result += f"Register: {register}, Values: [{reg_values}]\n"
		result += f"Free Registers: {', '.join(str(reg) for reg in self.free_regs) if self.free_regs else 'None'}"
		return result

#   def get_registers_having(self,value):
#     reg_set = []
#     for register, vals in self.registers.items():
#       if value in vals:
#         reg_set.append(register)
#     return reg_set
	

  