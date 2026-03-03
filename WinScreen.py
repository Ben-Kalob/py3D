from vectors import Vector2
import tkinter

class Window :
    
    size : list = Vector2(640,480)
    
    def __init__(self,size : Vector2):
        self.root = tkinter.Tk("Test01",sync=True)
        self.canvas = tkinter.Canvas(self.root,background="grey")
        self.frame = tkinter.Frame(self.root,background="white")
        self.set_size(size)
        self.canvas.pack()
        self.frame.pack()
        self.canvas.create_polygon((0,0),(50,50),(0,50),fill="red")
        self.elements = []
        self.x_offset = 0 #size.get_x()/2
        self.y_offset = 0 #size.get_y()/2
        
    def set_size(self,size : Vector2) :
        self.root.config(width=size.get_x(),height=size.get_y())
        self.root.grid(size.get_x(),size.get_y(),1,1)
        self.canvas.config(width=size.get_x(),height=size.get_y())
        self.root.wm_maxsize(width=size.get_x(),height=size.get_y())
        self.root.wm_minsize(width=size.get_x(),height=size.get_y())

    def clear_render(self) :
        self.canvas.delete("all")

    def full_clear(self) :
        for element in self.elements :
            element.destroy()
            self.elements = []

    def refresh(self) :
        self.root.update()