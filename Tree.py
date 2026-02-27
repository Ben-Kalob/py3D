import tkinter
from vectors import Vector2
from image_handler import load_image

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