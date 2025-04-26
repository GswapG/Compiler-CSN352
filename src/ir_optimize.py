import os
import re
from collections import defaultdict

class IROptimizer:
  def __init__(self,filename:str):
    self.IR = None
    self.optimized_ir = []
    self.constant_table = defaultdict(lambda:None)
    filename = filename[:-1]
    filename += 'tac'
    self.ir_path = os.path.join('./generatedIR' , filename)
    with open(self.ir_path,'r') as file:
      self.IR = file.read()
      
    # self.constant_propagation()
    self.constant_folding()
    self.write_optimized_ir()

  def constant_folding(self):
    for line in self.IR.splitlines():
      line = line.strip()
      if not line:
        self.optimized_ir.append("")
        continue
      instruction = line.split()
      if len(instruction) == 6:
        # t0 = 1 (int) + 2
        vars = instruction[2] , instruction[5]
        op = instruction[4]
        if self.is_constant(vars[0]) and self.is_constant(vars[1]):
          rhs = self.evaluate_constants(op,vars[0],vars[1])
          if rhs is not None:
            instruction = instruction[:2]
            instruction.append(rhs)
            print(rhs,'rhs')
      opt = ' '.join(instruction)
      self.optimized_ir.append(opt)
      

  def constant_propagation(self):
    '''Parsing the IR to get only instructions and ignore labels and funcs'''
    for line in self.IR.splitlines():
      line = line.strip()
      if not line:
        self.optimized_ir.append('')
        continue
      
      if '=' in line:
        '''For the moment only doing constant propagation and folding so we can ignore any other kind of instruction'''
        instruction = line.split() #HACKY MAKE SURE TO USE REGEX TO IGNORE SPACES INSIDE QUOTES
        instruction_vars = []
        for var in instruction:
          if self.is_var(var):
            instruction_vars.append(var)
        
        for i in range(len(instruction)):
          if i>0 and instruction[i] in instruction_vars and self.constant_table[instruction[i]]:
            instruction[i] = self.constant_table[instruction[i]]
            print(instruction[i])
           
        if len(instruction_vars) == 1:
          self.constant_table[instruction_vars[0]] =  instruction[-1]
        
        if len(instruction_vars) in (2,3):
          # x = 1 + y
          if self.constant_table[instruction_vars[1]] == None:
            self.constant_table[instruction_vars[0]] = None
          else:
            #self.evaluate_operands(line.split('=')[1])
            self.constant_table[instruction_vars[0]] = None  #for now ONLY!! #WRITE EVALUATE METHOD

        optimized_line = " ".join(instruction)
        
        self.optimized_ir.append(optimized_line)

      else:
        self.optimized_ir.append(line)

  def write_optimized_ir(self):
    with open(self.ir_path,'w') as file:
      for line in self.optimized_ir:
        file.write(line+'\n')
  
  def is_var(self,instruction_entry:str):
    if instruction_entry.startswith('@') or '#' in instruction_entry:
      return True
    return False
  
  def is_constant(self, var: str) -> bool:# Remove any whitespace
    var = var.strip()
    # Check for character literal ('x')
    if len(var) == 3 and var[0] == "'" and var[2] == "'":
        return True
        
    try:
        float(var)
        return True
    except ValueError:
        return False
  
  def evaluate_operands(self,instruction_rhs:str):
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