import os
import re
from .address_map import AddressMap
from .size_map import SizeMap
from .param_map import ParameterMap
from .type_map import TypeMap
from collections import defaultdict
from .utils import get_size_from_type

class IROptimizer:
	def __init__(self, filename: str ,typemap: TypeMap , var_type_map, address_map: AddressMap, size_map: SizeMap, param_map: ParameterMap):
		self.IR = None
		self.optimized_ir = []
		self.temp_count = 0
		self.address_map = address_map
		self.size_map = size_map
		self.param_map = param_map
		self.type_map = typemap
		self.var_type_map = var_type_map
		self.constant_table = defaultdict(lambda: None)
		filename = filename[:-1]
		filename += 'tac'
		self.ir_path = os.path.join('./generatedIR', filename)

		with open(self.ir_path, 'r') as file:
			self.IR = file.read()
		
	# self.constant_propagation()
		self.constant_folding()
		self.resolve_ptrs()
		self.write_optimized_ir()
		self.temp_update()


	def constant_folding(self):
		for line in self.IR.splitlines():
			line = line.strip()
			if not line:
				self.optimized_ir.append("")
				continue
			instruction = line.split()
			if len(instruction) == 6:
				# t0 = 1 (int) + 2
				vars = instruction[2], instruction[5]
				op = instruction[4]
				if self.is_constant(vars[0]) and self.is_constant(vars[1]):
					rhs = self.evaluate_constants(op, vars[0], vars[1])
					if rhs is not None:
						instruction = instruction[:2]
						instruction.append(rhs)
						print(rhs, 'rhs')
			opt = ' '.join(instruction)
			self.optimized_ir.append(opt)
		self.IR = '\n'.join(self.optimized_ir)
		self.optimized_ir = []

	def resolve_ptrs(self):
		for line in self.IR.splitlines():
			print(line)
			line = line.strip()
			if not line:
				self.optimized_ir.append("")
				continue
			if '=' not in line.split(' '):
				print('1')
				self.optimized_ir.append(line)
				continue
			instruction = line.split(' = ')
			lhs = instruction[0]
			lhs = lhs.split(' ')
			print(instruction)
			instruction = instruction[1].split(' ')
			for i in range(len(instruction)):
				if instruction[i].startswith('*') and instruction[i] != '*' and 'To' not in instruction[i]:
					code = f"@tt{self.temp_count} = {instruction[i]}"
					old = instruction[i]
					self.optimized_ir.append(code)
					instruction[i] = f"@tt{self.temp_count}"
					self.temp_count += 1
					old = old[1:]
					if old.startswith('@'):
						self.type_map.set_var(instruction[i],self.type_map.get_var(old)[1:])
					else:
						self.type_map.set_var(instruction[i],self.var_type_map.get_var(old)[1:])
			mod_inst = lhs + ['='] + instruction
			self.optimized_ir.append(' '.join(mod_inst))
		self.IR = '\n'.join(self.optimized_ir)
		self.optimized_ir = []

	def temp_update(self):
		next_line_gives_size = False
		offset_counter = 0
		current_func_name = None
		total_func_size = {}

		for line in self.IR.splitlines():
			line = line.strip()
			if line.startswith("."):
				next_line_gives_size = True
				current_func_name = line[1:-1]
				continue

			if next_line_gives_size:
				_, size = line.split(' ')

				offset_counter = int(size)
				next_line_gives_size = False

				parameters = self.param_map.get_params(current_func_name)
				for param, param_type in parameters:
					size = get_size_from_type(param_type)
					self.size_map.add_var(param, size)
					self.address_map.add_var(param, offset_counter + size)
					offset_counter += size

				continue 

			if line.startswith("@"):
				temp_var = line.split(' = ')[0]
				# get the type from type_map 
				type = self.type_map.get_var(temp_var)
				size = get_size_from_type(type)
				self.size_map.add_var(temp_var, size)
				self.address_map.add_var(temp_var, offset_counter + size)
				offset_counter += size
			
			if line.startswith("EndFunc"):
				total_func_size[current_func_name] = offset_counter

		for func_name, func_size in total_func_size.items():
			self.size_map.add_var(func_name, func_size)

	def constant_propagation(self):
		'''Parsing the IR to get only instructions and ignore labels and funcs'''
		for line in self.IR.splitlines():
			line = line.strip()
			if not line:
				self.optimized_ir.append('')
				continue
			
			if '=' in line:
				'''For the moment only doing constant propagation and folding so we can ignore any other kind of instruction'''
				instruction = line.split()  # HACKY MAKE SURE TO USE REGEX TO IGNORE SPACES INSIDE QUOTES
				instruction_vars = []
				for var in instruction:
					if self.is_var(var):
						instruction_vars.append(var)
				
				for i in range(len(instruction)):
					if i > 0 and instruction[i] in instruction_vars and self.constant_table[instruction[i]]:
						instruction[i] = self.constant_table[instruction[i]]
						print(instruction[i])
				
				if len(instruction_vars) == 1:
					self.constant_table[instruction_vars[0]] = instruction[-1]
				
				if len(instruction_vars) in (2, 3):
					# x = 1 + y
					if self.constant_table[instruction_vars[1]] == None:
						self.constant_table[instruction_vars[0]] = None
					else:
						# self.evaluate_operands(line.split('=')[1])
						self.constant_table[instruction_vars[0]] = None  # for now ONLY!! #WRITE EVALUATE METHOD

				optimized_line = " ".join(instruction)
				
				self.optimized_ir.append(optimized_line)

			else:
				self.optimized_ir.append(line)

	def write_optimized_ir(self):
		"""
		Writes the contents of self.IR to the file and prints it.
		"""
		with open(self.ir_path, 'w') as f:
			for line in self.IR.splitlines():
				if line[-1] == ':':
					if line[0] == '.':
						f.write(line + '\n')
					else:
						line = '\t' + line
						f.write(line + '\n')
				else:
					line = '\t\t' + line
					f.write(line + '\n')
		
		# Print the contents of self.IR
		# print(self.IR)

	def is_var(self, instruction_entry: str):
		if instruction_entry.startswith('@') or '#' in instruction_entry:
			return True
		return False
	
	def is_constant(self, var: str) -> bool:  # Remove any whitespace
		var = var.strip()
		# Check for character literal ('x')
		if len(var) == 3 and var[0] == "'" and var[2] == "'":
			return True
			
		try:
			float(var)
			return True
		except ValueError:
			return False
	
	def evaluate_operands(self, instruction_rhs: str):
		'''Will Return da evaluation of RHS'''
		pass

	def evaluate_constants(self, op: str, val1: str, val2: str) -> str:
		# Convert character literals to their ASCII values
		if len(val1) == 3 and val1[0] == "'" and val1[2] == "'":
			val1 = str(ord(val1[1]))
		if len(val2) == 3 and val2[0] == "'" and val2[2] == "'":
			val2 = str(ord(val2[1]))

		try:
			num1 = float(val1)
			num2 = float(val2)
			
			# Perform the operation
			result = {
				'+': num1 + num2,
				'-': num1 - num2,
				'*': num1 * num2,
				'/': num1 / num2 if num2 != 0 else None,
				'%': num1 % num2 if num2 != 0 else None
			}.get(op)
			
			if result is None:
				return None
			
			if result.is_integer():
				return str(int(result))
			return str(result)
			
		except (ValueError, TypeError):
			return None