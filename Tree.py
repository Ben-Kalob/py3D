import tkinter
from vectors import Vector2
from vectors import Vector3

from image_handler import load_image
import math
import qmath as quick_math
from Colourz import color
import Meshes

def get_function_from_path(node_path : str,function_name : str,current_instance) -> any :
    if not node_path.__contains__("$") :
        focus_node : object = current_instance
        if node_path.__contains__(".") :
            for path in node_path.split(".") :
                focus_node = getattr(focus_node,path)
        elif node_path != "" :
            focus_node = getattr(focus_node,node_path)
        return getattr(focus_node,function_name)
    else:
        objects_list : list = node_path.split(".")
        focus_node : Node = current_instance.world.get_node(objects_list[0].replace("$",""))
        objects_list.remove(objects_list[0])
        for node in objects_list :
            focus_node = focus_node.get_child(node)
        return getattr(focus_node,function_name)

class Node() :

    def __init__(self,name):
        self.name = name
        self.parent : Node = None
        self.children : dict = {}
    
    def add_child(self,node) :
        self.children[node.name] = node
        node.parent = self

    def get_child(self,name : str) -> any :
        try :
            return self.children[name]
        except :
            return None
    
    def global_position() -> Vector3 :
        return Vector3() ##defaults to empty

    def global_rotation() -> Vector3 :
        return Vector3() ##defaults to empty

    def destroy(self) :
        for child in self.children :
            self.children[child].destroy()
        self.children = {}
        self = None

class Node2D(Node) :

    instances : list = []

    def __init__(self, name):
        self.position = Vector2()
        self.visible = True
        Node2D.instances.append(self)
        super().__init__(name)
    
    def move_x(self,x : float) :
        self.position.set_x(self.position.get_x() + x)
    
    def move_y(self,y : float) :
        self.position.set_y(self.position.get_y() + y)
    
    def destroy(self):
        Node2D.instances.remove(self)
        return super().destroy()

class Sprite2D(Node2D) :
    def __init__(self, name,img_path,scale : float = 1):
        self.img_path = img_path
        self.image_scale : float = scale
        self.image_data : tkinter.PhotoImage = load_image(self.img_path,self.image_scale)
        super().__init__(name)

class Node3D(Node) :

    class_objects : list = []

    def __init__(self,object_name):
        self.name = object_name
        self.position = Vector3()
        self.rotation = Vector3()
        self.visible = True
        self.scale = 1
        Node3D.class_objects.append(self)
        super().__init__(object_name)

    def destroy(self):
        Node3D.class_objects.remove(self)
        return super().destroy()

    def global_position(self) -> Vector3 :
        if self.parent != None and isinstance(self.parent,Node3D) :
            return self.position + self.parent.global_position()
        else : 
            return self.position

    def global_rotation(self) -> Vector3 :
        if self.parent != None and isinstance(self.parent,Node3D) :
            return self.rotation + self.parent.global_rotation()
        else : 
            return self.rotation

    def rotate_x(self,angle,should_wrap : bool = False) :
        new_x = self.rotation.get_x()+angle
        if should_wrap :
            new_x = quick_math.wrapf(angle,0,360)
        self.rotation.set_x(new_x)

    def rotate_y(self,angle,should_wrap : bool = False) :
        new_y = self.rotation.get_y()+angle
        if should_wrap :
            new_y = quick_math.wrapf(new_y,0,360)
        self.rotation.set_y(new_y)

    def rotate_z(self,angle,should_wrap : bool = False) :
        new_z = self.rotation.get_z()+angle
        if should_wrap :
            new_z = quick_math.wrapf(angle,0,360)
        self.rotation.set_z(new_z)
    
    def move_x(self,distance) :
        new_x = self.position.get_x() + distance
        self.position.set_x(new_x)

    def move_y(self,distance) :
        new_y = self.position.get_y() + distance
        self.position.set_y(new_y)

    def move_z(self,distance) :
        new_z = self.position.get_z() + distance
        self.position.set_z(new_z)

class Light3D(Node3D) :

    all_lights : list[Light3D] = []

    def __init__(self, object_name,energy : float,size : float = 10):
        self.energy = energy
        self.size = size
        self.all_lights.append(self)
        super().__init__(object_name)

class BillBoard3D(Node3D) :
    def __init__(self,object_name,img_path : str):
        self.img_path = img_path
        self.image : tkinter.PhotoImage = load_image(img_path)
        self.image_scale = math.sqrt(pow(self.image.width(),2) + pow(self.image.height(),2)) /200

        super().__init__(object_name)

class Mesh3D(Node3D) :

    def __init__(self,object_name,mesh : Meshes.Mesh,color : color):
        self.mesh = mesh
        self.color = color

        super().__init__(object_name)

class Floor3D(Node3D) :

    def __init__(self, object_name,size = Vector2(5,5),obj_color = color(0.2,0.2,0.2)):

        super().__init__(object_name)

        for x in range(int(size.get_x())) :
            for y in range(int(size.get_y())) :
                node : Mesh3D = Mesh3D(f"floor_{x}_{y}",Meshes.PlaneMesh(),obj_color)
                node.position = self.position - Vector3(size.get_x()/2,0,size.get_y()/2)
                node.move_x(x )
                node.move_z(y )
                self.add_child(node)
                

        

class PhysicsBody(Node3D) :
    
    physic_instances : list[PhysicsBody] = []

    def __init__(self, object_name):
        PhysicsBody.physic_instances.append(self)
        self.velocity = Vector3()  ##note: VELOCITY IS RELATIVE TO THE ANGLE OF THE OBJECT!!!
        super().__init__(object_name)
    
    def process() :
        for body in PhysicsBody.physic_instances :
            body.position += body.velocity.rotated_around_y_axis(body.global_rotation().get_y())
            if isinstance(body,PlayerBody) :
                body.velocity = Vector3()
    
    def set_x_velocity(self,value) :
        self.velocity.set_x(value)

    def set_y_velocity(self,value) :
        self.velocity.set_y(value)
    
    def set_z_velocity(self,value) :
        self.velocity.set_z(value)
    


class PlayerBody(PhysicsBody) :
    pass
    

class WorldCamera(Node3D) :

    def __init__(self, object_name):
        self.name = object_name
        
        self.focal = 1/1300
        self.near_cull_distance = 0.05
        self.far_cull_distance = 25
        
        super().__init__(object_name)