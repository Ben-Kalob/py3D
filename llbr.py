import time
import math
import os
import json
import tkinter
from tkinter import ttk
from PIL import ImageTk, Image
import pywinstyles

class quick_math() :
    
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
        return (radian * 180) * quick_math.one_div_pi

    def deg_to_rad(degree : float) -> float :
        return (degree * math.pi)  * quick_math.rtdv

def parse_bool(string : str) -> bool :
    if string.lower() == "true" :
        return True
    else :
        return False

def get_real_path(path : str) :
    return os.path.dirname(os.path.realpath(__file__)).replace("\\","/") + "/" + path

def load_image(img_path : str,scale : float = 1) -> ImageTk.PhotoImage :
    np : str = get_real_path(img_path)
    img = Image.open(np)
    if scale >= 0.01 :
        scale = quick_math.clampf(scale,0.1,5)
        img = img.resize(size = (int(img.width*scale),int(img.height*scale)),resample=0)
    return ImageTk.PhotoImage(image=img)

def get_function_from_path(node_path : str,function_name : str) -> any :
    if not node_path.__contains__("$") :
        focus_node : object = Engine.current_instance
        if node_path.__contains__(".") :
            for path in node_path.split(".") :
                focus_node = getattr(focus_node,path)
        elif node_path != "" :
            focus_node = getattr(focus_node,node_path)
        return getattr(focus_node,function_name)
    else:
        objects_list : list = node_path.split(".")
        focus_node : Node = Engine.current_instance.world.get_node(objects_list[0].replace("$",""))
        objects_list.remove(objects_list[0])
        for node in objects_list :
            focus_node = focus_node.get_child(node)
        return getattr(focus_node,function_name)

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

class Window() :

    size : list = Vector2(640,480)

    def __init__(self,size : Vector2):
        self.root = tkinter.Tk("Test01",sync=True)
        self.canvas = tkinter.Canvas(self.root,background="blue")
        self.frame = tkinter.Frame(self.root,background="white")
        self.set_size(size)
        self.canvas.pack()
        self.frame.pack()
        self.elements = []

    def set_size(self,size : Vector2) :
        self.root.config(width=size.get_x(),height=size.get_y())
        self.root.grid(size.get_x(),size.get_y(),1,1)
        self.canvas.config(width=size.get_x(),height=size.get_y())
        self.root.wm_maxsize(width=size.get_x(),height=size.get_y())
        self.root.wm_minsize(width=size.get_x(),height=size.get_y())
    
    def full_clear(self) :
        for element in self.elements :
            element.destroy()
            self.elements = []

    def refresh(self) :
        self.root.update()

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

class INPUTKEY :
    
    def __init__(self, key_name,window : Window,func = None,process : bool = False,persist : bool = False):
        self.key = key_name
        self.is_pressed = False
        self.window = window
        self.process = process
        self.persist = persist
        self.press_bind = window.root.bind("<KeyPress-%s>" % self.key, self.press)
        self.release_bind = window.root.bind("<KeyRelease-%s>" % self.key, self.release)
        self.tied_function : function = func

    def press(self,_extra) :
        self.is_pressed = True
        if not self.process and self.tied_function != None :
            self.tied_function()
    
    def release(self,_extra) :
        self.is_pressed = False
    
    def destroy(self) :
        self.window.root.unbind("<KeyPress-%s>" % self.key, self.press_bind)
        self.window.root.unbind("<KeyRelease-%s>" % self.key, self.release_bind)
        self = None

class World() :

    active_world = None

    def __init__(self):
        self.Nodes : list = {}
        World.active_world = self

    def clear(self) :
        for node in self.Nodes :
            self.Nodes[node].destroy()
        self.Nodes = {}

    def get_node(self,node_name : str) :
        return self.Nodes[node_name]

    def register_node(self,node : Node) :
        self.Nodes[node.name] = node

    def node(self,data : dict) :
        node = Node(data["name"])
        self.Nodes[data["name"]] = node

    def sprite2d(self,data : dict) :
        scale : float = 1
        if data.__contains__("scale") :
            scale = data["scale"]
        node = Sprite2D(data["name"],data["img"],scale)
        position : list = data["pos"]
        node.position = Vector2(position[0],position[1])
        self.register_node(node)

class InputHandler() :

    def __init__(self,window):
        self.inputs : list[INPUTKEY] = []
        self.window = window
    
    def bind_input(self,info : dict) :
        command = info["func"].split(";",3)
        try : 
            func_instance = get_function_from_path(command[0],command[1])
            func = None
            if len(command) >= 3 :
                arg = command[2]
                try : arg = json.loads(arg)
                except : pass
                func = lambda : func_instance(arg)
            else: func = func_instance
        except : func = None
        process_mode : bool = False
        if info.__contains__("process") :
            process_mode = parse_bool(info["process"])
        persist : bool = False
        if info.__contains__("persist") :
            persist = parse_bool(info["persist"])
        
        key : INPUTKEY = INPUTKEY(info["key"],self.window,func,process=process_mode,persist=persist)
        self.inputs.append(key)
    
    def process(self) :
        for key in self.inputs :
            if key.process and key.is_pressed :
                key.tied_function()

    def clear(self) :
        for key in self.inputs :
            if not key.persist :
                key.destroy()
        self.inputs = []
    
class Engine() :

    current_instance = None

    def __init__(self) :
        Engine.current_instance = self
        config = self.load_config()
        self.window = Window(size=Vector2.parse(config["win_size"]))
        self.world = World()
        self.current_script = config["starting_script"]
        self.input = InputHandler(self.window)
        self.element_assembler = ElementAssembler(self)
        self.running = True
        self.frame_time = 1/float(config["frame_rate"])
        self.process_functions : list = []
        self.start()
    
    def quit(self) :
        self.window.root.destroy()
        self.running = False

    def start(self) :
        
        self.load_script(self.current_script)

        delta : float = 0
        previous_time : float = -1

        while self.running :
            self.process(delta,previous_time)
    
    def Draw2D(self) :
        self.window.canvas.delete("all")
        for node in Node2D.instances :
            if node.visible :
                if type(node) == Sprite2D :
                    self.window.canvas.create_image(node.position.get_x(),node.position.get_y(),image=node.image_data)

    def load_config(self) -> dict :
        conf = json.loads(open(get_real_path("conf.lbls")).readline())
        print(f"configurement: {conf}")
        return conf

    def clear(self) :
        self.window.full_clear()
        self.world.clear()
        self.input.clear()

    def load_script(self,path) :

        self.clear()
        
        self.current_script = path
        real_path = get_real_path(path)
        
        lines : list[dict] = []
        with open(real_path) as file:
            for line in file :
                if not line.__contains__("#") and not line.strip() == "" :
                    lines.append(json.loads(line.rstrip()))

        for data in lines :
            if data.__contains__("type") :
                if data["type"] == "gui" :
                    if hasattr(self.element_assembler,data["class"]) :
                        getattr(self.element_assembler,data['class'])(data)
                elif data["type"] == "input" :
                    self.input.bind_input(data)
                elif data["type"] == "func" :
                    command : list = data["path"].split(";",3)
                    func = get_function_from_path(command[0],command[1])
                    if data.__contains__("process") and parse_bool(data["process"]) :
                        if len(command) > 2 :
                            try : arg = json.loads(command[2])
                            except : arg = command[2]
                            self.process_functions.append(lambda : func(arg))
                        else:
                            self.process_functions.append(lambda : func())
                    else:
                        if len(command) > 2 :
                            func(command[2])
                        else:
                            func()
                elif data["type"] == "obj" :
                    class_name = data["class"].lower()
                    if hasattr(self.world,class_name) :
                        getattr(self.world,class_name)(data)

    def process(self,delta : float,previous_time : float) :

        previous_time = time.time()

        self.window.root.focus_force()

        for func in self.process_functions : func()

        self.input.process()
        self.Draw2D()
        self.window.refresh()

        delta = time.time() - previous_time
        
        if delta < self.frame_time :
            time.sleep(self.frame_time-delta)
        
class ElementAssembler() :

    transparent_color : str = "#000001"

    def __init__(self,engine : Engine):
        self.engine = engine
        self.window = engine.window
    
    def text(self,data : dict) :
        position : Vector2 = Vector2.parse(data["pos"])
        font : str = None
        if data.__contains__("font") :
            font = data["font"]
        font_size : int = 12
        if data.__contains__("font_size") :
            font_size = data["font_size"]
        text = tkinter.Label(self.window.root,text=data["text"],anchor="center",font=(font,font_size),bg=ElementAssembler.transparent_color)
        pywinstyles.set_opacity(text,color=ElementAssembler.transparent_color)
        text.place(x=position.get_x(),y=position.get_y())
        self.window.elements.append(text)

    def button(self,data : dict) :
        position : Vector2 = Vector2.parse(data["pos"])
        function_instance = None
        if data.__contains__("command") :
            command : list = data["command"].split(";",3)
            tied_function : function = get_function_from_path(command[0],command[1])
            if len(command) > 2 : function_instance = lambda : tied_function(command[2])
            else : function_instance = lambda : tied_function()
        font = None
        if data.__contains__("font") :
            font = data["font"]
        font_size : int = 12
        if data.__contains__("font_size") :
            font_size = data["font_size"]
        button = tkinter.Button(self.window.root,text=data["text"],command= function_instance,font=(font,font_size),cursor="hand2")
        button.place(x=position.get_x(),y=position.get_y())
        self.window.elements.append(button)

main = Engine()

print("engine finished")
