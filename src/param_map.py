from collections import defaultdict
from exceptions import *
from utils import get_size_from_type

class ParameterMap:
  def __init__(self):
    '''A Map which stores parameters for a func with name and type info of a param'''
    self.f_params = defaultdict(list,lambda:None)

  def add_param(self,func:str,params:list[tuple[str,str]]):
    '''Add parameter to default dict straight forward'''
    self.f_params[func] = params

  def get_params(self,func:str) -> list[tuple[str,str]]:

    if self.f_params[func] is None:
      raise CompileException("Invalid access")
    return self.f_params[func]
  
  def get_size_list(self,func:str) -> list[int]:
    temp = []
    for p in self.f_params[func]:
      temp.append(get_size_from_type(p[1]))
    return temp
  

'''
Below Code to be added to parser driver , not adding to avoid merge conflict from mmukul's semantics:


param_map = ParameterMap()
for entry in symtab.table_entries:
    if entry.kind != 'function':
        continue
    param_list = symtab.search_params(entry.name)
    push_list = []
    for param in param_list:
        push_list.append((param.name,param.type))
    param_map.add_param(push_list)

'''
