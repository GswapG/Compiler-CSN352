class CompileException(Exception):
    pass

class CompileValueError(CompileException):
    pass

class CompileTypeError(CompileException):
    pass