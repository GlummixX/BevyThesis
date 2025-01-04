from . import OGLBuffers
from OpenGL.GL import *


class OBJLoader:
    def __init__(self, model_path):
        self.vData = []  # List of Vertex Coordinates f32
        self.vtData = [] # List of Texture Coordinates f32
        self.vnData = [] # List of Normal Coordinates f32
        self.fv = [] # Face Vertex Indices i32
        self.ft = [] # Face Texture Indices i32
        self.fn = [] # Face Normal Indices i32
        self.load_obj_model(model_path)
        self.set_face_render_type()
    
    def load_obj_model(self, model_path):
        try:
            print("Reading model file ", model_path, end = "")
            # Open a file handle and read the models data
            with open(model_path, "r") as f:
                file = f.readlines()
            for line in file:
                if line[0] == "#": continue
                elif line == "": continue 
                    # Ignore whitespace data
                elif line[0:2] == "v ": 
                    # Read in Vertex Data
                    self.vData.append(self.process_data(line))
                elif line[0:3] == "vt ": 
                    # Read Texture Coordinates
                    self.vtData.append(self.process_data(line))
                elif line[0:3] == "vn ":
                    # Read Normal Coordinates
                    self.vnData.append(self.process_data(line))
                elif line[0:2] == "f ": 
                    # Read Face (index) Data
                    self.process_face_data(line)
                
            print("OBJ model: ", model_path, "... read")
        except Exception as e:
            print("Failed to find or read OBJ: ", model_path)
            print(e)
   

    def process_data(self, read:str):
        s = read.split()
        return (self.process_float_data(s)) 

    def process_float_data(self, sdata):
        data = [None]*(len(sdata)-1)
        for loop in range(0, len(data)):
            data[loop] = float(sdata[loop + 1])
        return data 

    def process_face_data(self, fread:str):
        s = fread.split()
        if "#" in fread: 
            # Pattern is present if obj has only v and vn in face data
            for loop in range(1, len(s)):
                s[loop] = s[loop].replaceAll("#", "/1/") 
                # insert a zero for missing vt data
        self.process_fint_data(s) # Pass in face data

    def process_fint_data(self, sdata):           
        vdata = [None]*3
        vtdata = [None]*3
        vndata = [None]*3

        for loop in range(1, len(sdata)):
            s = sdata[loop]
            temp = s.split("/")
            index = loop - 1
            if (loop > 3):	#make a new triangle as a triangle fan
                self.fv.append(vdata)		#save previous triangle
                self.ft.append(vtdata)
                self.fn.append(vndata)
                
                vdataN = [None]*3
                vtdataN = [None]*3
                vndataN = [None]*3

                vdataN[0] = vdata[0] #first vertex always at index 0
                vtdataN[0] = vtdata[0]
                vndataN[0] = vndata[0]
                
                vdataN[1] = vdata[2] #second vertex is the third one of previous triangle 
                vtdataN[1] = vtdata[2]
                vndataN[1] = vndata[2]
                index = 2
                
                vdata = vdataN 
                vtdata = vtdataN
                vndata = vndataN
            
            vdata[index] = int(temp[0]) 
            # always add vertex indices

            if len(temp) > 1:# if true, we have v and vt data
                vtdata[index] = int(temp[1]) 
                # add in vt indices
            else:
                vtdata[index] = 0 # if no vt data is present fill in zeros
            if len(temp) > 2: # if true, we have v, vt, and vn data
                vndata[index] = int(temp[2]) 
                # add in vn indices
            else:
                vndata[index] = 0# if no vn data is present fill in zeros
        self.fv.append(vdata)
        self.ft.append(vtdata)
        self.fn.append(vndata)

    def set_face_render_type(self):
        self.topology = GL_TRIANGLES 
        
class OGLModelOBJ:
    
    def get_vertices_buffer(self):
        return self.vertices_buffer

    def get_normals_buffer(self):
        return self.normals_buffer

    def get_tex_coords_buffer(self):
        return self.tex_coords_buffer

    def get_buffers(self):
        return self.buffer

    def get_topology(self):
        return self.topology

    def __init__(self, model_path):
        self.vertices_buffer = None
        self.normals_buffer = None
        self.tex_coords_buffer = None
        
        loader = OBJLoader(model_path) 
        self.topology = loader.topology
        
        print(len(loader.fv), len(loader.fv[0]))
        if loader.fv[0][0] > 0:
            self.vertices_buffer = []

            c3 = 1
            for i in range(0, len(loader.fv)):
                for j in range(0,len(loader.fv[i])):
                    c0 = loader.vData[loader.fv[i][j] - 1][0] # x
                    c1 = loader.vData[loader.fv[i][j] - 1][1] # y
                    c2 = loader.vData[loader.fv[i][j] - 1][2] # z
                    self.vertices_buffer.append((c0,c1,c2,c3))

        if loader.ft[0][0] > 0:
            self.tex_coords_buffer = []
            for i in range(0,len(loader.ft)):
                for j in range(0, len(loader.ft[i])):
                    self.tex_coords_buffer.append(loader.vtData[loader.ft[i][j] - 1][0])
                    self.tex_coords_buffer.append(loader.vtData[loader.ft[i][j] - 1][1])

        if loader.fn[0][0] > 0:
            self.normals_buffer = []

            for i in range(0, len(loader.fn)):
                for j in range(0,len(loader.fn[i])):
                    c0 = loader.vnData[loader.fn[i][j] - 1][0] # x
                    c1 = loader.vnData[loader.fn[i][j] - 1][1] # y
                    c2 = loader.vnData[loader.fn[i][j] - 1][2] # z
                    self.normals_buffer.append((c0,c1,c2))
    
        self.buffer = self.to_ogl_buffers(self.vertices_buffer, self.normals_buffer, self.tex_coords_buffer)

    
    def to_ogl_buffers(self, verticesBuf, normalsBuf, texCoordsBuf):
        if verticesBuf is not None:
            attributesPos = [OGLBuffers.Attrib("inPosition", 4)]
            buffers = OGLBuffers.OGLBuffers(verticesBuf, None, attributesPos)
        else:
            return None

        if texCoordsBuf is not None:
            attributesTexCoord = [OGLBuffers.Attrib("inTexCoord", 2)]
            buffers.add_vertex_buffer(texCoordsBuf, attributesTexCoord)
            
        if normalsBuf is not None:
            attributesNormal = [OGLBuffers.Attrib("inNormal", 3)]
            buffers.add_vertex_buffer(normalsBuf, attributesNormal)
            
        return buffers
