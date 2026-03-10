##NOTES
##make .exe file with [pyinstaller "C:\Users\justl\Programs\Python projects\Py3D.py"] command (need pyinstaller)

import math

from Tree import *

import qmath as quick_math

from Colourz import color

from WinScreen import Window
from image_handler import load_image

from vectors import Vector3

import Meshes

class BUFFERED_OBJ() :
    def __init__(self,data : list = [],type = None,world_position : Vector3 = Vector3(),normal : Vector3 = Vector3()):
        self.data : list = data
        self.world_position : Vector3 = world_position
        self.type = type
        self.z_score : float = 0
        self.light_energy : float = 0
        self.normal : Vector3 = normal

camera : WorldCamera = None

class Engine3D() :

    current = None

    def __init__(self,window,engine):
        Engine3D.current = self
        self.engine = engine
        self.window : Window = window

def get_normal_dir(from_point : Vector3,to_point : Vector3) -> Vector3 :
    x_dir = 0
    y_dir = 0
    z_dir = 0

    if from_point.get_x() < to_point.get_x() : x_dir = -1
    else : x_dir = 1

    if from_point.get_y() < to_point.get_y() : y_dir = -1
    else : y_dir = 1

    if from_point.get_z() < to_point.get_z() : z_dir = -1
    else : z_dir = 1

    return Vector3(x_dir,y_dir,z_dir)

def Draw3D() :
    
    if camera == None :
        return 

    #Engine .canvas.delete("all") ##clear screen
    draw_queue : list[BUFFERED_OBJ] = []
    for object in Node3D.class_objects :
        if object.visible :
            calc_object(object,draw_queue)
            #obj_thread = Thread(target=calc_object,args=(object,draw_queue))
            #threads.append(obj_thread)
    
    for obj in draw_queue :
        #centriod = [average([points[0][0],points[1][0],points[2][0]]),average([points[0][1],points[1][1],points[2][1]]),average([points[0][2],points[1][2],points[2][2]])]
        #I don't really understand how this ended up working, I just kept trying stuff till it work :\
        
        #max([points[0][2],points[1][2],points[2][2]]) + min([points[0][2],points[1][2],points[2][2]]) + average([points[0][1],points[1][1],points[2][1]]) + average([points[0][2],points[1][2],points[2][2]]) - max([points[0][1],points[1][1],points[2][1]])
        
        if obj.type == BillBoard3D : ##add billboard
            pos = obj.data[1]
            obj.z_score = 2 * pos.get_z()
        elif obj.type == Mesh3D :
            obj.z_score = calc_z_score(obj.data[0])
    
    for light in Light3D.all_lights :
        for obj in draw_queue :
            if obj.type == Mesh3D :
                dis : float = distance(light.global_position(),obj.world_position)
                if dis <= light.size :
                    
                    direction = get_normal_dir(light.global_position(),obj.world_position)
                    
                    diff = average([abs(direction.get_x()+obj.normal.get_x()),abs(direction.get_y()+obj.normal.get_y()),abs(direction.get_z()+obj.normal.get_z())])

                    power = light.energy / (dis/light.size)
                    obj.light_energy += power * diff

                    #diff = distance(obj.normal,direction)
                    #print(diff)

                    #    power = light.energy / (dis/light.size)
                    #    obj.light_energy += power

    for obj in sorted(draw_queue, key = lambda x :x.z_score,reverse=True) : ##sorted based on "z score"
        if obj.type == Mesh3D :
            
            mod_color : color = obj.data[1]
            mod_color *= obj.light_energy

            draw_triangle(obj.data[0],mod_color)

        elif obj.type == BillBoard3D :

            position = screen_plot(obj.data[1])

            if not type(position) == bool :

                st : BillBoard3D = obj.data[2]

                scale = ( st.image_scale/obj.z_score  ) * st.scale

                st.image = load_image(st.img_path,scale)

                if ( position[0] > st.image.width() * -0.5 and position[1] < Window.root.winfo_screenwidth() ) :

                    Engine3D.current.engine.window.canvas.create_image(position[0],position[1],image = st.image)
                    
def calc_z_score(points : list[Vector3]) :
    #centriod = Vector3(average([points[0].get_x(),points[1].get_x(),points[2].get_x()]),average([points[0].get_y(),points[1].get_y(),points[2].get_y()]),average([points[0].get_z(),points[1].get_z(),points[2].get_z()]))
    y_list = [points[0].get_y(),points[1].get_y(),points[2].get_y()]
    z_list = [points[0].get_z(),points[1].get_z(),points[2].get_z()]
    score =  min(z_list) + max(z_list) + (max(y_list)-min(y_list)) + min(y_list) - max(y_list)
    return score
        
def calc_object(object,draw_queue : list):

    if type(object) is Mesh3D :

        object_mesh : Meshes.Mesh = object.mesh
        
        for face_index in range(len(object_mesh.point_order)) :
            calc_face(object_mesh.point_order[face_index],object,object_mesh,face_index,draw_queue)

    elif type(object) is BillBoard3D :
        np = combine_vec3(object.global_position(),camera.global_position(),True)
        cam_rot = combine_vec3(Vector3(),camera.global_rotation(),True) ##invert 
        np = transform_rotation(np,cam_rot)

        if np.get_z() < camera.far_cull_distance and np.get_z() > camera.near_cull_distance * 4 :
            draw_queue.append(BUFFERED_OBJ(data=[object.image,np,object],type=BillBoard3D,world_position=object.global_position()))
        
def calc_face(face,object : Node3D,object_mesh : Meshes.Mesh,face_index,face_obj : list) -> any :
    tri : list[Vector3] = [Vector3.parse(object_mesh.vertex_point[face[0]-1]),Vector3.parse(object_mesh.vertex_point[face[1]-1]),Vector3.parse(object_mesh.vertex_point[face[2]-1])]

    position : Vector3 = combine_vec3(object.global_position(),camera.global_position(),True)
    rotation : Vector3 = object.global_rotation()

    scale = object.scale

    tri = [transform_scale(tri[0],scale),transform_scale(tri[1],scale),transform_scale(tri[2],scale)]

    tri = [transform_rotation(tri[0],rotation),transform_rotation(tri[1],rotation),transform_rotation(tri[2],rotation)]

    tri = [transform_position(tri[0],position),transform_position(tri[1],position),transform_position(tri[2],position)]

    ##camera rotation has to be applied after the first in order to work correctly
    cam_rot = combine_vec3(Vector3(),camera.global_rotation(),True) ##inverts
    
    tri = [transform_rotation(tri[0],cam_rot),transform_rotation(tri[1],cam_rot),transform_rotation(tri[2],cam_rot)]

    dis = max([tri[0].get_z(),tri[1].get_z(),tri[2].get_z()])

    ##if behind camera, skip rendering ##pretty important
    if dis < camera.near_cull_distance :
        return None
    
    ##currently using a distance based shader where in it is brighter the closer an object is - it's not great
    
    color = object.color 

    if dis < camera.far_cull_distance :
        face_obj.append(BUFFERED_OBJ(data=[tri,color,object_mesh],type=Mesh3D,world_position=object.global_position(),normal=transform_rotation(Vector3(object_mesh.normal_vectors[face_index]),rotation)))
        return face_obj
    
    face_index += 1

def draw_triangle(triangle : list,color : color,fill : bool = True) -> bool :

    start_point = screen_plot(triangle[0])
    if not start_point : return False
    mid_point = screen_plot(triangle[1])
    if not mid_point : return False
    end_point = screen_plot(triangle[2])
    if not end_point : return False
    
    ##draw if at least one point is on screen
    if is_point_on_screen(start_point) or is_point_on_screen(mid_point) or is_point_on_screen(end_point) :
        Engine3D.current.window.canvas.create_polygon(start_point,mid_point,end_point,fill=color.get_hex())
        return True

def is_point_on_screen(point : tuple) :
    win_size : Vector2 = Engine3D.current.window.size
    margin : int = 20
    
    if point[0] < -margin : return False
    if point[0] > win_size.get_x() + margin : return False

    if point[1] < -margin : return False
    if point[1] > win_size.get_y() + margin : return False

    return True

def screen_plot(point : Vector3) -> any : ##returns either a boolean or a tuple for rendering
    ##usually it's /focal but it is set to 1/value to help skip the division for every tri
    f = (point.get_z()*camera.focal)
    if f <= 0 :
        return False
    df = 1/f
    new_point = ((point.get_x())*df + Engine3D.current.window.x_offset,(-point.get_y())*df + Engine3D.current.window.y_offset)
    return new_point

def transform_position(point : Vector3 ,position : Vector3) -> Vector3 :
    
    new_point = Vector3(point.get_x() + position.get_x(),point.get_y() + position.get_y(),point.get_z() + position.get_z())
    
    return new_point

def transform_rotation(point : Vector3, rotation : Vector3) -> Vector3 :

    z : Vector3 = rotate_2D_Vec(Vector2(point.get_x(),point.get_y()),quick_math.deg_to_rad(rotation.get_z()))
    new_point = Vector3(z.get_x(),z.get_y(),point.get_z())
    ## 0 1 2
    ## 0 1 2

    y : Vector3 = rotate_2D_Vec(Vector2(new_point.get_x(),new_point.get_z()),quick_math.deg_to_rad(rotation.get_y()))
    new_point = Vector3(y.get_x(),new_point.get_y(),y.get_y())
    ## 0 2 1
    ## 0 1 1

    x : Vector3 = rotate_2D_Vec(Vector2(new_point.get_y(),new_point.get_z()),quick_math.deg_to_rad(rotation.get_x()))
    new_point = Vector3(new_point.get_x(),x.get_x(),x.get_y())
    ## 0 2 0
    ## 0 0 1

    return new_point

def distance(point_1 : Vector3, point_2 : Vector3) -> float :
    return math.sqrt( pow(point_2.get_x() - point_1.get_x(),2) + pow(point_2.get_y() - point_1.get_y(),2) + pow(point_2.get_z() - point_1.get_z(),2) )

def transform_scale(point : Vector3,scale) -> Vector3 :
    point = Vector3(point.get_x()*scale,point.get_y()*scale,point.get_z()*scale)
    return point

def rotate_2D_Vec(vector : Vector2,angle : float) -> Vector2 :
    
    s = math.sin(angle)
    c = math.cos(angle)

    x = c * vector.get_x() - s * vector.get_y()
    y = s * vector.get_x() + c * vector.get_y()

    return Vector2(x,y)

def total(values : list) -> float :
    total : float = 0
    for value in values :
        total += value
    return total

def average(values : list) -> float :
    return total(values) / len(values)

def combine_vec3(l1 : Vector3, l2 : Vector3, subtract : bool = False) -> Vector3 :

    multi : int = 1

    if subtract : multi = -1

    x = l1.get_x() + l2.get_x() * multi
    y = l1.get_y() + l2.get_y() * multi
    z = l1.get_z() + l2.get_z() * multi

    return Vector3(x,y,z)
