import json

class Vector2() :

    def __init__(self,x:float = 0.0,y:float = 0.0):
        self.point = [x,y]
    
    def set_x(self,value : float) :
        self.point[0] = value
    
    def set_y(self,value : float) :
        self.point[1] = value

    def get_x(self) -> float :
        return self.point[0]
    
    def get_y(self) -> float :
        return self.point[1]
    
    def parse(value) :
        if type(value) == list or type(value) == tuple :
            return Vector2(value[0],value[1])
        elif type(value) == str :
            n_value = json.loads(value)
            return Vector2.parse(n_value)
        else:
            print("ERROR: INVALID PARSE")

    def __str__(self):
        return str(self.point)

class Vector3() :

    def __init__(self,x:float = 0.0,y:float = 0.0,z:float = 0.0):
        self.point = [x,y,z]
    
    def set_x(self,value : float) :
        self.point[0] = value
    
    def set_y(self,value : float) :
        self.point[1] = value

    def set_z(self,value : float) :
        self.point[2] = value

    def get_x(self) -> float :
        return self.point[0]
    
    def get_y(self) -> float :
        return self.point[1]

    def get_z(self) -> float :
        return self.point[2]
    
    def parse(value) :
        if type(value) == list or type(value) == tuple :
            return Vector3(value[0],value[1],value[2])
        elif type(value) == str :
            n_value = json.loads(value)
            return Vector3.parse(n_value)
        else:
            print("ERROR: INVALID PARSE")

    def __str__(self):
        return str(self.point)