from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
from pyglutils import OGLUtils, ShaderUtils, OGLTextRenderer
import glfw
import numpy as np
from OpenGL.GL import *
import random
from __main__ import PATH

class Renderer(Abstract_renderer):
    """author PGRF FIM UHK
        version 2.0-PY
        rewrite: Matěj Kolář
        since 10-2022
    """

    def __init__(self):
        self.data_size = 8*(1+3+3+1) 
        self.data = np.zeros(self.data_size,dtype=np.float32)
        self.data_out = np.zeros(self.data_size,dtype=np.float32)
        
        self.offset = 4
        self.compute = 0

        
    def key_callback(self, window, key, scancode, action, mods):
            if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
                glfw.set_window_should_close(window, True) # We will detect this in the rendering loop

    def ws_callback(self, window, w, h):
            if w > 0 and h > 0 and (w != self.width or h != self.height):
                self.width = w
                self.height = h
                if self.textRenderer is not None:
                    self.textRenderer.resize(self.width, self.height)
                    
    def cp_callback(self, window, x, y):
        pass

    def init(self):
        OGLUtils.print_OGL_parameters()
        
        self.compute_shader_program = ShaderUtils.load_program_specific(None, None, None, None, None, 
                PATH+"shaders/lvl2advanced/p06compute/p02buffer/computeBuffer") 
        
        
        self.loc_offset = glGetUniformLocation(self.compute_shader_program, "offset")

        # buffer initialization
        for i in range(0,self.data_size):
            self.data[i] = random.random()
        
        print("Input Data values")
        for i in range(0,self.data_size):
            if i % 8 == 0:
                print()
            print(round(self.data[i],2), end=" ")
        print()

        # declare and generate a buffer object name
        self.loc_buffer= glGenBuffers(2)
        
        # bind the buffer and define its initial storage capacity
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[0])
        glBufferData(GL_SHADER_STORAGE_BUFFER, self.data, GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.loc_buffer[0])
        
        # bind the buffer and define its initial storage capacity
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[1])
        glBufferData(GL_SHADER_STORAGE_BUFFER, self.data_out, GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.loc_buffer[1])
        
        # unbind the buffer
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
        
        #assign the index of shader storage block to the binding point (see shader)  
        glShaderStorageBlockBinding(self.compute_shader_program, 0, 0) #input buffer
        glShaderStorageBlockBinding(self.compute_shader_program, 1, 1) #output buffer
        
        print("key values: ",end="")
        for i in range(0,self.data_size,8):
            print(round(self.data[i],4),end=" ")
        print("")
        
        text = __name__ + " nothing to render, see console output"
        
        print(text)
        
        self.textRenderer = OGLTextRenderer(self.width, self.height)
    
    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        if self.offset > 0:
            glUseProgram(self.compute_shader_program)

            glUniform1i(self.loc_offset, int(self.offset))
                    
            #set input and output buffer
            if self.compute % 2 == 0:
                #bind input buffer
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[0])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.loc_buffer[0])
                
                #bind output buffer
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[1])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.loc_buffer[1])
                
            else:
                #bind input buffer
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[1])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.loc_buffer[1])
                #bind output buffer
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[0])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.loc_buffer[0])
            
            glDispatchCompute(int(self.offset), 1, 1)
            
            # make sure writing to image has finished before read
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            
        if self.compute < 3:    
            if self.compute % 2 == 0:
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[1])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.loc_buffer[1])
            else:
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.loc_buffer[0])
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, self.loc_buffer[0])

            self.data_out = np.zeros(self.data_size*4,dtype=np.uint8)
            self.data_out = glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.data_size*4, self.data_out)
            self.data_out = self.data_out.view("<f4")
            print("Output data values after iteration ", (self.compute+1), " offset ", self.offset, end="")
            for i in range(0,self.data_size):
                if i % 8 == 0:
                    print("")
                print(round(self.data_out[i],2),end=" ")
            print("")

            if self.offset <= 1:
                print("minimal key value is", round(self.data_out[0],2))
            
            self.compute+=1
            self.offset = self.offset/2
            
        
        glUseProgram(0)
        
        glClearColor(0.5, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        text = __name__ + " nothing to render, see console output"
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
 