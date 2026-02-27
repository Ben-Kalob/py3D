##input handler

import json
from WinScreen import Window
from parser import parse_bool
from Tree import get_function_from_path

class InputKey :
    
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

class InputHandler() :

    def __init__(self,window,engine):
        self.inputs : list[InputKey] = []
        self.window = window
        self.engine_instance = engine
    
    def bind_input(self,info : dict) :
        command = info["func"].split(";",3)
        try : 
            func_instance = get_function_from_path(command[0],command[1],self.engine_instance)
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
        
        key : InputKey = InputKey(info["key"],self.window,func,process=process_mode,persist=persist)
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