from collections import defaultdict
from .exceptions import *
from .utils import get_size_from_type

class ParameterMap:
  def __init__(self):
    '''A Map which stores parameters for a func with name and type info of a param'''
    self.f_params = defaultdict(list)

  def add_param(self,func:str,params:list[tuple[str,str]]):
    '''Add parameter to default dict straight forward'''
    self.f_params[func] = params

  def get_params(self,func:str) -> list[tuple[str,str]]:
    '''Get the parameters for a function, if not found return empty list'''
    if self.f_params[func] is None:
      return []
    return self.f_params[func]
  
  def get_size_list(self,func:str) -> list[int]:
    temp = []
    for p in self.f_params[func]:
      temp.append(get_size_from_type(p[1]))
    return temp

  def __str__(self):
    """
    Returns a string representation of the ParameterMap's state.
    """
    result = "Parameter Map:\n"
    for func, params in self.f_params.items():
        param_list = ', '.join(f"({name}, {type_})" for name, type_ in params)
        result += f"Function: {func}, Parameters: [{param_list}]\n"
    return result