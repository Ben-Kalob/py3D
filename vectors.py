import json
import math
import qmath

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

    def rotate(self,angle) :

        s = math.sin(angle)
        c = math.cos(angle)

        x = c * self.get_x() - s * self.get_y()
        y = s * self.get_x() + c * self.get_y()

        return Vector2(x,y)

    def __str__(self):
        return str(self.point)

class Vector3() :

    def __init__(self,x:float = 0.0,y:float = 0.0,z:float = 0.0):
        if type(x) == list or type(x) == tuple : ##parse from list
            self.point = [x[0],x[1],x[2]]
        else : ##basic three points provided
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
    
    def rotated_around_y_axis(self,angle : float) :
        angle = qmath.deg_to_rad(angle)
        rotated_point : Vector2 = Vector2(self.get_x(),self.get_z()).rotate(angle)
        return Vector3(rotated_point.get_x(),self.get_y(),rotated_point.get_y())

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

    def __add__(self, other):
        if type(other) == Vector3 :
            return Vector3(self.point[0]+other.point[0],self.point[1]+other.point[1],self.point[2]+other.point[2])
    
    def __sub__(self, other):
        if type(other) == Vector3 :
            return Vector3(self.point[0]-other.point[0],self.point[1]-other.point[1],self.point[2]-other.point[2])

    def __iadd__(self, other):
        return self.__add__(other)


