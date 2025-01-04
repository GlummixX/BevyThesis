from transforms import Vec2D, Vec3D
from pyglutils import OGLBuffers, OGLUtils, ShaderUtils, OGLTextRenderer
from pyglutils.ShaderUtils import GEOMETRY_SHADER_SUPPORT_VERSION
import random
import sys
from OpenGL.GL import *
from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
import glfw
from __main__ import PATH

class Renderer(Abstract_renderer):
    """ author: PGRF FIM UHK
        PY rewrite: Matěj Kolář
        version: 2.0-PY
        since: 10-2022
    """
    
    def __init__(self):
        self.update = True
        self.mode = False
    
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if (action == glfw.PRESS or action == glfw.REPEAT):
            if key == glfw.KEY_R:
                self.init_buffers()
                self.update = True
            elif key == glfw.KEY_M:
                self.mode =not self.mode

    def ws_callback(self, window, w, h):
        self.window = window
        if w > 0 and h > 0 and (w != self.width or h != self.height):
            self.width = w
            self.height = h
            if self.textRenderer is not None:
                self.textRenderer.resize(self.width, self.height)

    def mb_callback(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            x,y = glfw.get_cursor_pos(window)
            mouseX = (x / self.width) * 2 - 1
            mouseY = ((self.height - y) / self.height) * 2 - 1
            self.index_buffer_data.append(len(self.index_buffer_data))
            self.vertex_buffer_data_pos.append(Vec2D(mouseX, mouseY))
            self.vertex_buffer_data_col.append(Vec3D(mouseX / 2 + 0.5, mouseY / 2 + 0.5, 1))
            self.update = True

    def init_buffers(self):
        self.index_buffer_data = []
        self.vertex_buffer_data_pos = []
        self.vertex_buffer_data_col = []
        
        self.vertex_buffer_data_pos.append(Vec2D(-0.5, 0.0))
        self.vertex_buffer_data_pos.append(Vec2D(0.0, 0.5))
        self.vertex_buffer_data_pos.append(Vec2D(0.0, -0.5))
        self.vertex_buffer_data_pos.append(Vec2D(0.5, 0.0))
        self.vertex_buffer_data_pos.append(Vec2D(0.7, 0.5))
        self.vertex_buffer_data_pos.append(Vec2D(0.9, -0.7))
        
        for i in range(0, len(self.vertex_buffer_data_pos)):
            self.index_buffer_data.append(i)
            self.vertex_buffer_data_col.append(Vec3D(random.random(), random.random(), random.random()))

 
    
    def update_buffers(self):
        attributes_pos = [OGLBuffers.Attrib("inPosition", 2)]
        attributes_col = [OGLBuffers.Attrib("inColor", 3)]
        
        self.buffers = OGLBuffers.OGLBuffers(self.vertex_buffer_data_pos, None, attributes_pos, self.index_buffer_data)
        self.buffers.add_vertex_buffer(self.vertex_buffer_data_col, attributes_col)

    
    def init(self):
        OGLUtils.shader_check()
        if (OGLUtils.get_version_GLSL() < GEOMETRY_SHADER_SUPPORT_VERSION):
            print("Geometry shader is not supported") 
            sys.exit(1)
        
        OGLUtils.print_OGL_parameters()
        
        glClearColor(0.2, 0.2, 0.2, 1.0)

        ext = str(glGetString(GL_EXTENSIONS))
        if not "GL_ARB_enhanced_layouts" in ext:
            self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p01geometryshader/geometry_OlderSM")
        else:
            self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p01geometryshader/geometry")
        
        self.init_buffers()
        self.textRenderer = OGLTextRenderer(self.width, self.height)

    

    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        if self.update:
            self.update_buffers()
            self.update = False
            print(len(self.index_buffer_data))
        
        
        if self.mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glUseProgram(self.shader_program)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        self.buffers.draw(GL_LINE_STRIP_ADJACENCY, self.shader_program, len(self.index_buffer_data))
        
        text = __name__ + ": [M]ode"
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
