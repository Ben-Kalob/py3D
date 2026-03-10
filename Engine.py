import time
import json
import tkinter
from tkinter import ttk
from PIL import ImageTk, Image
import pywinstyles

import qmath

from WinScreen import Window

from SysNav import get_real_path

from pypit import InputHandler

from vectors import Vector2

from parser import *

from Colourz import color

import py3D
import Meshes

from Tree import get_function_from_path
from Tree import *

class World() :

    active_world = None

    def __init__(self):
        self.Nodes : dict = {}
        World.active_world = self

    def clear(self) :
        for node in self.Nodes :
            self.Nodes[node].destroy()
        self.Nodes = {}

    def get_node(self,node_name : str) :
        return self.Nodes[node_name]

    def register_node(self,node : Node,data : dict) :
        if data.__contains__("parent") : ##if assigned to parent, make that connection
            parent_node : Node = self.get_node(data["parent"])
            parent_node.add_child(node)
        else: ##otherwise, add to tree
            self.Nodes[node.name] = node

    def node(self,data : dict) :
        node = Node(data["name"])
        self.register_node(node,data)

    def sprite(self,data : dict) :
        scale : float = 1
        if data.__contains__("scale") :
            scale = data["scale"]
        node = Sprite2D(data["name"],data["img"],scale)
        position : list = data["pos"]
        node.position = Vector2(position[0],position[1])
        self.register_node(node,data)
    
    def set_up_node3d(self,node,data : dict) :
        if data.__contains__("pos") :
            node.position = Vector3(data["pos"])
        if data.__contains__("rot") :
            node.rotation = Vector3(data["rot"])

    def playerbody(self,data : dict) :
        node : PlayerBody = PlayerBody(data["name"])
        self.set_up_node3d(node,data)
        self.register_node(node,data)

    def camera(self,data : dict) :
        node : WorldCamera = WorldCamera(data["name"])
        self.set_up_node3d(node,data)
        py3D.camera = node
        self.register_node(node,data)

    def node3d(self,data : dict) :
        node : Node3D = Node3D(data["name"])
        self.set_up_node3d(node,data)
        self.register_node(node,data)
    
    def mesh(self,data : dict) :
        obj_color = color(0)
        if data.__contains__("color") :
            obj_color = color(data["color"])
        node : Mesh3D = Mesh3D(data["name"],Meshes.mapper[data["mesh"]](),obj_color)
        self.set_up_node3d(node,data)
        self.register_node(node,data)

    def light(self,data : dict) :
        power : float = 1
        range : float = 10
        if data.__contains__("power") :
            power = data["power"]
        if data.__contains__("range") :
            range = data["range"]
        node = Light3D(data["name"],power,range)
        self.set_up_node3d(node,data)
        self.register_node(node,data)
    
    def floor(self,data : dict) :
        size = Vector2()
        if data.__contains__("size") :
            size = Vector2.parse(data["size"])
        obj_color = color(0)
        if data.__contains__("color") :
            obj_color = color(data["color"])
        node = Floor3D(data["name"],size,obj_color)
        self.set_up_node3d(node,data)
        self.register_node(node,data)
    
class Engine() :

    current_instance = None

    def __init__(self) :
        Engine.current_instance = self
        config = self.load_config()
        self.window = Window(size=Vector2.parse(config["win_size"]))
        self.Engine3D = py3D.Engine3D(self.window,self)
        self.world = World()
        self.current_script = config["starting_script"]
        self.input = InputHandler(self.window,self)
        self.element_assembler = ElementAssembler(self)
        self.running = True
        self.frame_time = 1/float(config["frame_rate"])
        self.process_functions : list = []
        
        ##hacky fix to add frame display without adding it to the registor
        self.frame_display = self.element_assembler.text({"pos" : [0,0],"text" : "test", "color" : [1,1,1]})
        self.window.elements = []
        
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
        for node in Node2D.instances :
            if node.visible :
                if type(node) == Sprite2D :
                    self.window.canvas.create_image(node.position.get_x(),node.position.get_y(),image=node.image_data)

    def Draw3D(self) :
        py3D.Draw3D()

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
                    func = get_function_from_path(command[0],command[1],self)
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
                    else: print(f"type {class_name} does NOT exist")

    def process(self,delta : float,previous_time : float) :
        
        previous_time = time.time()

        self.window.canvas.focus_force()

        PhysicsBody.process() ##process physics

        for func in self.process_functions : func()

        self.input.process()
        
        self.window.clear_render()
        
        self.Draw3D()
        self.Draw2D()

        self.window.refresh()

        delta = time.time() - previous_time
        
        self.frame_display.config(text= "fps: " + str(round(1/delta,2)))

        if delta < self.frame_time :
            time.sleep(self.frame_time-delta)
        
class ElementAssembler() :

    transparent_color : str = "#000001"

    def __init__(self,engine : Engine):
        self.engine = engine
        self.window = engine.window
    
    def text(self,data : dict) -> any :
        position : Vector2 = Vector2.parse(data["pos"])
        font : str = None
        if data.__contains__("font") :
            font = data["font"]
        font_size : int = 12
        if data.__contains__("font_size") :
            font_size = data["font_size"]
        text_color = color(0)
        if data.__contains__("color") :
            text_color = color(data["color"])
        text_obj = tkinter.Label(self.window.root,text=data["text"],anchor="center",font=(font,font_size),bg=ElementAssembler.transparent_color,foreground=text_color.get_hex())
        pywinstyles.set_opacity(text_obj,color=ElementAssembler.transparent_color)
        text_obj.place(x=position.get_x(),y=position.get_y())
        self.window.elements.append(text_obj)
        return text_obj

    def button(self,data : dict) :
        position : Vector2 = Vector2.parse(data["pos"])
        function_instance = None
        if data.__contains__("command") :
            command : list = data["command"].split(";",3)
            tied_function : function = get_function_from_path(command[0],command[1],Engine.current_instance)
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
