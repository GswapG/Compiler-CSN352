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
      
    self.parse_ir()
    self.write_optimized_ir()

  def parse_ir(self):
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
  
  def evaluate_operands(self,instruction_rhs:str):
    '''Will Return da evaluation of RHS'''
    pass