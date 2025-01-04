from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
from pyglutils import OGLBuffers, OGLUtils, ShaderUtils, OGLTexture2D, OGLTextRenderer
from OpenGL.GL import *
from __main__ import PATH
import glfw


class Renderer(Abstract_renderer):
    """author: PGRF FIM UHK
        version: 2.0-PY
        rewrite: Matěj Kolář
        since: 10-2022
    """

    def __init__(self):
        self.mode = 0
        self.tex_w = 256
        self.tex_h = 256
        

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if (action == glfw.PRESS or action == glfw.REPEAT):
            if key == glfw.KEY_M:
                self.mode = (self.mode+1) % 3

    
    def ws_callback(self, window, w, h):
            if (w > 0 and h > 0 and (w != self.width or h != self.height)):
                self.width = w
                self.height = h
                if (self.textRenderer != None):
                    self.textRenderer.resize(self.width, self.height)

    def create_buffer(self):
        vertex_buffer_data = [
                -1, -1, 	0.7, 0, 0, 	0, 0,
                 1,  0,		0, 0.7, 0,	0, 1,
                 0,  1,		0, 0, 0.7, 	1, 0 ]
        index_buffer_data = [ 0, 1, 2 ]

        attributes = [
                OGLBuffers.Attrib("inPosition", 2),
                OGLBuffers.Attrib("inColor", 3),  
                OGLBuffers.Attrib("inTexCoord", 2, 5) ]
        self.buffers = OGLBuffers.OGLBuffers( vertex_buffer_data, 7, attributes, index_buffer_data)
        
        print(self.buffers)
    
    def init(self):
        OGLUtils.print_OGL_parameters()
        
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p06compute/p01intro/drawImage")
        self.compute_shader_program = ShaderUtils.load_program_specific(None, None, None, None, None, 
                PATH+"shaders/lvl2advanced/p06compute/p01intro/computeImage") 
        
        
        self.create_buffer()

        self.loc_mode = glGetUniformLocation(self.compute_shader_program, "mode")
    
        self.texture_viewer = OGLTexture2D.Viewer()

        self.tex_output = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_output)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.tex_w,self.tex_h, 0, GL_RGBA, GL_FLOAT, None)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        
        #Limits on work group size per dimension
        for dim in range(0,3):
            val = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, dim)
            print("GL_MAX_COMPUTE_WORK_GROUP_SIZE [", dim,  "] : ", val)
        
        self.textRenderer = OGLTextRenderer(self.width, self.height)

    
    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        glBindImageTexture (0, self.tex_output, 0, False, 0, GL_WRITE_ONLY, GL_RGBA32F)
                        
        #fill texture in compute shader
        glUseProgram(self.compute_shader_program)
        
        glUniform1i(self.loc_mode, self.mode%3) 
        
        glDispatchCompute(8,8,1)
        
        # make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        #show result texture by textureViewer
        self.texture_viewer.view(self.tex_output, -1, 0, 0.5, 1., -1)
                
        #draw result texture by shader program
        glUseProgram(self.shader_program) 
        
        glBindImageTexture (0, self.tex_output, 0, False, 0, GL_READ_ONLY, GL_RGBA32F)
        
        # draw
        self.buffers.draw(GL_TRIANGLES, self.shader_program)
        
        
        text = __name__ + " [m]ode: " + str(self.mode)
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")