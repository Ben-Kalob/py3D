import qmath as quick_math

class color() :

    def __init__(self,r : float, g : float, b : float):
        self.r = r
        self.g = g
        self.b = b

    def copy(self) -> object :
        return color(self.r,self.g,self.b)
    
    def __mul__(self, value):
        return color(self.r*value,self.g*value,self.b*value)

    def __imul__(self,value) :
        return self.__mul__(value)

    def get_hex(self) :
        
        r = quick_math.clampf(self.r * 255,0,255)
        g = quick_math.clampf(self.g * 255,0,255)
        b = quick_math.clampf(self.b * 255,0,255)

        return '#%02x%02x%02x' % (int(r),int(g),int(b))  ##converts to hex

    def __str__(self):
        return str((self.r,self.g,self.b))