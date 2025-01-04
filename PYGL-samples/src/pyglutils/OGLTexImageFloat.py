import copy
from OpenGL.GL import *
import numpy as np

class Format():
    def __init__(self, component_count):
        self.component_count = component_count

    def get_internal_format(self):
        if self.component_count == 1:
            return GL_R32F
        elif self.component_count == 2:
            return GL_RG32F
        elif self.component_count == 3:
            return GL_RGB32F
        elif self.component_count == 4:
            return GL_RGBA32F
        else:
            return -1

    def get_pixel_format(self):
        if self.component_count == 1:
            return GL_RED
        elif self.component_count == 2:
            return GL_RG
        elif self.component_count == 3:
            return GL_RGB
        elif self.component_count == 4:
            return GL_RGBA
        else:
            return -1

    def get_pixel_type(self):
        return GL_FLOAT

    def get_component_count(self):
        return self.component_count

    def buffer(self, buf):
        return buf

    def new_buffer(self, width, height, depth = 1):
        return np.zeros((width * height * depth * self.component_count),dtype=np.float32)

    def new_tex_image(self, width, height, depth = 1):
        return OGLTexImageFloat().from_format(width, height, depth, self)

class FormatDepth(Format):
    def __init__(self):
        super(1)

    def get_internal_format(self):
        return GL_DEPTH_COMPONENT
    
    def get_pixel_format(self):
        return GL_DEPTH_COMPONENT

    def get_pixel_type(self):
        return GL_FLOAT

class FormatIntensity(Format):
    def __init__(self):
        super(1)
    
    def get_internal_format(self):
        return 1

    def get_pixel_format(self):
        return GL_LUMINANCE

    def get_pixel_type(self):
        return GL_FLOAT
class OGLTexImageFloat():
    def __init__(self):
        pass

    def from_component_count_no_depth(self, width:int, height:int, component_count:int, data = None):
        self.from_format(width, height, 1, OGLTexImageFloat.Format(component_count),data)
        return self

    def from_component_count(self, width:int, height:int, depth:int, component_count:int, data = None):
        self.from_format(width, height, depth, OGLTexImageFloat.Format(component_count), data)
        return self

    def from_format_no_depth(self, width:int, height:int, format, data = None):
        self.from_format(width, height, 1, format, data)
        return self

    def from_format(self, width:int, height:int, depth:int, format, data = None):
        self.width = width
        self.height = height
        self.depth = depth
        self.format = format
        if data is None:
            self.data = np.zeros(width*height*depth*format.get_component_count())
        else:
            self.data = np.array(data, dtype=np.float32)
        return self

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_depth(self):
        return self.depth

    def set_data_buffer(self, buffer):
        if len(buffer) == self.width * self.height * self.depth * self.format.get_component_count():
            self.data = copy.deepcopy(buffer)

    def get_data_buffer(self):
        return self.get_data()

    def get_format(self):
        return self.format

    def get_data(self):
        return self.data

    def to_OGL_tex_image_byte(self, component_count = None):
        if component_count is None:
            component_count = self.format.get_component_count()
        #array = np.zeros((self.width * self.height * component_count* self.height),dtype=np.ubyte)
        array = self.data*255
        #for (int z = 0 z < depth z++)
        #    for (int y = 0 y < height y++)
        #        for (int x = 0 x < width x++)
        #            for (int i = 0 i < componentCount i++)
        #                array[z * width * height * componentCount + y * width * componentCount + x * componentCount
        #                        + i] = (byte) (Math
        #                                .min(data[z * width * height * format.getComponentCount()
        #                                        + y * width * format.getComponentCount()
        #                                       + x * format.getComponentCount() + i % format.getComponentCount()], 1.0)
        #                                * 255.0)

        return OGLTexImageByte(self.width, self.height, self.depth, OGLTexImageByte.Format(component_count), array)

    def set_pixel(self, x, y, value):
        self.set_voxel_component(x, y, 0, 0, value)

    def set_pixel_component(self, x, y, component, value):
        self.set_voxel_component(x, y, 0, component, value)

    def set_voxel(self, x, y, z, value):
        self.set_voxel_component(x, y, z, 0, value)

    def set_voxel_component(self, x, y, z, component, value):
        if x >= 0 and x < self.width and y >= 0 and y < self.height and z >= 0 and z < self.depth and component >= 0 \
            and component < self.format.get_component_count():
            self.data[int((z * self.width * self.height + y * self.width + x) * self.format.get_component_count() + component)] = value

    def get_pixel(self, x, y):
        return self.get_voxel(x, y, 0, 0)

    def get_pixel(self, x, y, component):
        return self.get_voxel(x, y, 0, component)

    def get_voxel(self, x, y, z):
        return self.get_voxel(x, y, z, 0)

    def get_voxel(self, x, y, z, component):
        value = 0
        if x >= 0 and x < self.width and y >= 0 and y < self.height and z >= 0 and z < self.depth and component >= 0 \
            and component < self.format.get_component_count():
            value = self.data[(z * self.width * self.height + y * self.width + x) * self.format.get_component_count() + component]
        return value

    def flipY(self):
        for z in range(0,self.depth):
            for y in range(0,int(self.height/2)):
                for x in range(0,self.width):
                    for i in range(0, self.format.get_component_count()):
                        value = self.get_voxel(x, y, z, i)
                        self.set_voxel(x, y, z, i, self.get_voxel(x, self.height - y, z, i))
                        self.set_voxel(x, self.height - y, z, i, value)
