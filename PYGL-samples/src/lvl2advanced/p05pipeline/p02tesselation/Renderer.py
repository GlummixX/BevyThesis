from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
import glfw
from pyglutils import OGLBuffers, OGLUtils, ShaderUtils, OGLTextRenderer
from OpenGL.GL import *
from __main__ import PATH

class Renderer(Abstract_renderer):
    """ author PGRF FIM UHK
        version 2.0-PY
        rewrite: Matěj Kolář
        since 10-2022"""


    def __init__(self):
        self.stop = False
        self.demo_type_changed = True
        self.demo_type = 0
        self.time = 1
        self.buffers = None
        self.shader_program = None
        
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_S:
                self.stop = not self.stop

            elif key == glfw.KEY_M:
                self.demo_type = (self.demo_type+1) % 4
                self.demo_type_changed = True


    def ws_callback(self, window, w, h):
        if w > 0 and h > 0 and (w != self.width or h != self.height):
            self.width = w
            self.height = h
            if (self.textRenderer is not None):
                self.textRenderer.resize(self.width, self.height)

    def create_buffers(self):
        index_buffer_data = [0,1,2]
        
        vertex_buffer_data_pos = [
            -0.8, -0.9, 
            -0.8, 0.6,
            0.6, 0.8, 
        ]
        
        vertex_buffer_data_col = [
            0, 1, 0, 
            1, 0, 0,
            1, 1, 0,
        ]
        
        attributesPos = [OGLBuffers.Attrib("inPosition", 2)]
        
        attributesCol = [OGLBuffers.Attrib("inColor", 3)]
        
        self.buffers = OGLBuffers.OGLBuffers(vertex_buffer_data_pos, None ,attributesPos, index_buffer_data)
        self.buffers.add_vertex_buffer(vertex_buffer_data_col, attributesCol)
        
        print(self.buffers)

    
    def private_init(self, demo_type):
        ext = OGLUtils.get_extensions()
        new_shader_program = 0
        if demo_type == 0: #only VS a FS
            print("Pipeline: VS + FS")
            if "GL_ARB_enhanced_layouts" not in ext:
                new_shader_program = ShaderUtils.load_program_specific(
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel_OlderSM_WithoutGS",
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel_OlderSM_WithoutGS") 
            else:
                new_shader_program = ShaderUtils.load_program_specific(
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel",
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel")

        elif demo_type == 1: # only VS, FS and GS
            print("Pipeline: VS + GS + FS")
            if OGLUtils.get_version_GLSL() >= ShaderUtils.GEOMETRY_SHADER_SUPPORT_VERSION:
                if "GL_ARB_enhanced_layouts" not in ext:
                    new_shader_program = ShaderUtils.load_program_specific( 
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel_OlderSM_OnlyGS",
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel_OlderSM_OnlyGS", 
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel_OlderSM_OnlyGS") 
                else:
                    new_shader_program = ShaderUtils.load_program_specific( 
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel", 
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel",
                            PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel") 
            else:
                print("Geometry shader is not supported")
        elif demo_type == 2: #VS, FS and tess
            print("Pipeline: VS + tess + FS")
            if OGLUtils.get_version_GLSL() >= ShaderUtils.TESSELATION_SUPPORT_VERSION:
                new_shader_program = ShaderUtils.load_program_specific( 
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel",
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel",
                        None,
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel",
                        PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel") 

            else:
                print("Tesselation is not supported")
        else: #VS, FS, GS and tess
            print("Pipeline: VS + tess + GS + FS")
            if OGLUtils.get_version_GLSL() >= ShaderUtils.TESSELATION_SUPPORT_VERSION:
                new_shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p02tesselation/tessel")
            else:
                print("Tesselation is not supported")

        return new_shader_program	
        

    def init(self):
        if OGLUtils.get_version_GLSL() >= ShaderUtils.TESSELATION_SUPPORT_VERSION:
            max_patch_vertices = glGetIntegerv(GL_MAX_PATCH_VERTICES)
            print("Max supported patch vertices ", max_patch_vertices)
        
        self.create_buffers()
        self.textRenderer = OGLTextRenderer(self.width, self.height)

    

    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        if self.demo_type_changed:
            old_shader_program = self.shader_program
            self.shader_program = self.private_init(self.demo_type)
            if self.shader_program>0:
                pass
                #glDeleteProgram(old_shader_program)
            else:
                self.shader_program = old_shader_program
            self.locTime = glGetUniformLocation(self.shader_program, "time")
            self.demo_type_changed = False

        
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        glClearColor(0.2, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
        
        if not self.stop: self.time *= 1.01
        self.time =  self.time % 100
        
        #print(time)
        
        glUseProgram(self.shader_program) 
        glUniform1f(self.locTime, self.time) 
        
        if self.demo_type == 1: #points VS+GS+FS
            if OGLUtils.get_version_GLSL() >= 300:
                self.buffers.draw(GL_TRIANGLES, self.shader_program)
	
        elif self.demo_type == 2 or self.demo_type == 3: #tessellation VS+TCS+TES+FS #points VS+TCS+TES+GS+FS
            if OGLUtils.get_version_GLSL() >= 400:
                glPatchParameteri(GL_PATCH_VERTICES, 3)
                self.buffers.draw(GL_PATCHES, self.shader_program)
            	
        else: #triangle VS+FS
            self.buffers.draw(GL_TRIANGLES, self.shader_program) 
	
        
        text = __name__ + f": [I]nit, [M]ode {self.time}"
        
        if self.stop: text += " [S]tart"
        else: text += " [S]top"
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
