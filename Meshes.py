
##cube mesh
cube_vert = [(-0.5,0.5,0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(-0.5,0.5,-0.5),(-0.5,-0.5,0.5),(0.5,-0.5,-0.5),(0.5,-0.5,0.5),(-0.5,-0.5,-0.5)]
cube_order = [(1,3,5),(3,7,5),(2,4,6),(4,8,6),(3,2,7),(2,6,7),(4,1,8),(1,5,8),(3,1,2),(1,4,2),(5,7,8),(7,6,8)]
cube_normal = [(0,1,0),(0,1,0),(0,-1,0),(0,-1,0),(1,0,0),(1,0,0),(-1,0,0),(-1,0,0),(0,1,0),(0,1,0),(0,-1,0),(0,-1,0)]

##plane mesh
plane_vert = [(-0.5,0,0.5),(0.5,0,-0.5),(0.5,0,0.5),(-0.5,0,-0.5)]
plane_order = [(1,2,3),(2,4,1)]
plane_normal = [(0,1,0),(0,1,0)]

class Mesh() :
    def __init__(self):
        self.vertex_point : list = []
        self.point_order : list = []
        self.normal_vectors : list = []

class CubeMesh(Mesh) :
    def __init__(self):
        self.vertex_point = cube_vert
        self.point_order = cube_order
        self.normal_vectors = cube_normal

class PlaneMesh(Mesh) :
    def __init__(self):
        self.vertex_point = plane_vert
        self.point_order = plane_order
        self.normal_vectors = plane_normal

mapper : dict[function] = {
    "cube" : CubeMesh,
    "plane" : PlaneMesh
}