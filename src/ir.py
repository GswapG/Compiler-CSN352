class IR:
    def __init__(self):
        self.place = None
        self.code = ""
        self.truelist = []
        self.falselist = []
        self.nextlist = []
        self.switchup = []
        self.switchplace = []
        self.begin = ""
        self.after = ""
        self.parameters = []
        self.else_ = ""
        self.initializer_list = []
        self.array_dimension = 0
        self.array_sizes = []