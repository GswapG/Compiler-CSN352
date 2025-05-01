from collections import defaultdict

class TypeMap:
	def __init__(self):
		'''
		Stores STR->STR temp to type values
		'''
		self.type_map = defaultdict(str)

	def set_var(self, var:str , type:str):
		'''Used to set the type of the variable'''
		self.type_map[var] = type
	def get_var(self,var:str) -> str:
		'''Used to get the type of the temp_var'''
		return self.type_map[var]

	def __str__(self) -> str:
		"""
		Returns a string representation of the type map.
		Format:
		Variable | Type
		-----------------
		@t0     | int*
		@t1     | char
		etc.
		"""
		if not self.type_map:
			return "TypeMap: <empty>"
			
		# Find the longest variable name for proper alignment
		max_var_len = max((len(var) for var in self.type_map.keys()), default=0)
		
		# Create header
		header = f"{'Variable':<{max_var_len}} | Type\n"
		separator = "-" * max_var_len + "-+-" + "-" * 10 + "\n"
		
		# Create entries
		entries = ""
		for var, type_str in sorted(self.type_map.items()):
			entries += f"{var:<{max_var_len}} | {type_str}\n"
		
		return header + separator + entries