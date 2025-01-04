import numpy as np
from OpenGL.GL import *
from transforms import Vec2D, Vec3D

class Attrib:
    def __init__(self, name, dimension, normalize = False, offsetInFloats = None):
        self.name = name
        self.dimension = dimension
        if offsetInFloats is not None:
            self.offset = 4 * offsetInFloats
        else:
            self.offset = -1
        self.normalize = normalize
            
    def to_string(self):
        return f"new Attrib( /*name:*/ {self.name}, /*dimension:*/ {self.imension}, /*normalize:*/ {self.normalize}, /*offset:*/ {self.offset})"
    
class VertexBuffer:
    def __init__(self, id, stride, attributes):
        self.id = id
        self.stride = stride
        self.attributes = attributes
    
    def to_string(self):
        return(str(self))
    
class OGLBuffers:
    
    def __init__(self, vertexData, floatsPerVertex, attributes, indexData = None):
        self.indexCount = -1
        self.vertexCount = -1
        self.vertexBuffers = []
        self.attribArrays = []
        self.indexBuffer = 0
        
        self.add_vertex_buffer(vertexData, attributes, floatsPerVertex)
        if indexData is not None:
            self.set_index_buffer(indexData)
        

    def add_vertex_buffer(self, data, attributes, floatsPerVertex = None):
        if attributes == None or len(attributes) == 0:
            return

        if floatsPerVertex is None:
            floatsPerVertex = 0
            for i in range(0, len(attributes)):
                floatsPerVertex += attributes[i].dimension
        
        bufferID = glGenBuffers(1)
        if isinstance(data[0],Vec2D) or isinstance(data[0],Vec3D):
            data = [[*x] for x in data]
        buffer = np.array(data, dtype = np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, bufferID)
        glBufferData(GL_ARRAY_BUFFER, buffer, GL_STATIC_DRAW)

        if buffer.size % floatsPerVertex != 0:
            print("The total number of floats is incongruent with the number of floats per vertex.")
        if (self.vertexCount < 0):
            self.vertexCount = buffer.size / floatsPerVertex
        elif self.vertexCount != (buffer.size / floatsPerVertex):
            print("Warning: GLBuffers.addVertexBuffer: vertex count differs from the first one.")

        self.vertexBuffers.append(VertexBuffer(bufferID, floatsPerVertex * 4, attributes))

    def set_index_buffer(self, data):
        self.indexCount = len(data)
        indexBufferBuffer = np.array(data, dtype = np.uint32)
        self.indexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexBufferBuffer, GL_STATIC_DRAW)

    def bind(self, shaderProgram):
        if self.attribArrays is not None:
            for attrib in self.attribArrays:
                glDisableVertexAttribArray(attrib)
        self.attribArrays = []
        for vb in self.vertexBuffers:
            glBindBuffer(GL_ARRAY_BUFFER, vb.id)
            offset = 0
            for j in range(0, len(vb.attributes)):
                location = glGetAttribLocation(shaderProgram, vb.attributes[j].name)
                if (location >= 0): # due to optimization GLSL on a graphic card
                    self.attribArrays.append(location)
                    glEnableVertexAttribArray(location)
                    if vb.attributes[j].offset < 0:
                        ofst = offset
                    else:
                        ofst = vb.attributes[j].offset
                    glVertexAttribPointer(location, vb.attributes[j].dimension, GL_FLOAT, vb.attributes[j].normalize, vb.stride, ctypes.c_void_p(ofst))
                
                offset += 4 * vb.attributes[j].dimension
            

        if self.indexBuffer != 0:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)


    def unbind(self):
        if self.attribArrays is not None:
            for attrib in self.attribArrays:
                glDisableVertexAttribArray(attrib)
            self.attribArrays = None

    def draw(self, topology, shaderProgram, count = None, start = 0):
        if count is None:
            glUseProgram(shaderProgram)
            self.bind(shaderProgram)
            if self.indexBuffer == 0:
                glDrawArrays(topology, 0, int(self.vertexCount))
            else:
                glDrawElements(topology, self.indexCount, GL_UNSIGNED_INT, None)
            self.unbind()
        else:
            glUseProgram(shaderProgram)
            self.bind(shaderProgram)
            if self.indexBuffer == 0 :
                glDrawArrays(topology, start, count)
            else:
                glDrawElements(topology, count, GL_UNSIGNED_INT, ctypes.c_void_p(start * 4))
            self.unbind()

    def to_string(self):
        text = f"OGLBuffers, indexCount: {self.indexCount}, vertexCount:{self.vertexCount}"
        for vb in self.vertexBuffers:
            text += "\n\t" + vb.to_string() 
        return text