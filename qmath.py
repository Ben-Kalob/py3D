import math

pi : float = 3.14159

one_div_pi : float = 1/math.pi

rtdv = 1/180 ##rad to degree value - helps avoid division

def wrapf(value,min,max) -> float :

    if value < min :
        value = max + value

    elif value > max :
        value = value % max
    
    return value

def clampf(value,min,max) -> float :

    if value < min :
        value = min

    elif value > max :
        value = max
    
    return value

def rad_to_deg(radian : float) -> float :
    return (radian * 180) * one_div_pi

def deg_to_rad(degree : float) -> float :
    return (degree * math.pi)  * rtdv
