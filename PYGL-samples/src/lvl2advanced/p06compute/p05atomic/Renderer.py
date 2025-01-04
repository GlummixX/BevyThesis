from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
from pyglutils import ShaderUtils, OGLBuffers, OGLUtils, OGLTexture2D, OGLTextRenderer
import glfw
import math
from OpenGL.GL import *
import numpy as np
from __main__ import PATH

class Renderer(Abstract_renderer):
    """author PGRF FIM UHK
        version 2.0-PY
        rewrite: Matěj Kolář
        since 10-2022
    """

    def __init__(self):
        self.wg_size = [None]*3

        self.step = False
        self.fill = True
        self.first = 0
    
        self.mode = 0
        self.count = 256
        self.tex_w = 256
        self.tex_h = 256
        

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_M:
                self.mode += 1
                self.mode = self.mode% 4
                self.first = 0
            elif key == glfw.KEY_S:
                self.step = not self.step
                self.first = 0
            elif key == glfw.KEY_F:
                self.fill = not self.fill
                self.first = 0
            elif key == glfw.KEY_PAGE_UP:
                self.count =self.count/2
                if self.count<2: self.count =2
                self.first = 0
            elif key == glfw.KEY_PAGE_DOWN:
                self.count =self.count*2
                if self.count>32*2048: self.count = 32*2048
                self.first = 0
    

    def ws_callback(self, window, w, h):
        if w > 0 and h > 0 and (w != self.width or h != self.height):
            self.width = w
            self.height = h
            if self.textRenderer is not None:
                self.textRenderer.resize(self.width, self.height)
            self.first = 0

    def create_buffer(self):
        vertex_buffer_data = [
                -1, -1,  0.7, 0, 0,  0.0, 0.0,
                 1,  0,	 0, 0.7, 0,	 0, 1,
                 0,  1,	 0, 0, 0.7,  1, 0
            ]
        index_buffer_data = { 0, 1, 2 }

        attributes = [
                OGLBuffers.Attrib("inPosition", 2),
                OGLBuffers.Attrib("inColor", 3),  
                OGLBuffers.Attrib("inTexCoord", 2, 5)  ]
        self.buffers = OGLBuffers.OGLBuffers(vertex_buffer_data, 7, attributes, index_buffer_data)
        
        print(self.buffers)
    
    
    def create_buffer2(self):
        vertex_buffer_data = [None]*(self.count*3*7)
        
        for i in range(0,self.count):
            vertex_buffer_data[3*7*i+0+0] =  0
            vertex_buffer_data[3*7*i+0+1] =  0
            vertex_buffer_data[3*7*i+0+2] =  0
            vertex_buffer_data[3*7*i+0+3] =  0
            vertex_buffer_data[3*7*i+0+4] =  0
            vertex_buffer_data[3*7*i+0+5] =  0
            vertex_buffer_data[3*7*i+0+6] =  0

            vertex_buffer_data[3*7*i+7+0] =  math.cos(2*math.pi/self.count*i)
            vertex_buffer_data[3*7*i+7+1] =  math.sin(2*math.pi/self.count*i)
            vertex_buffer_data[3*7*i+7+2] =  0xF<<i
            vertex_buffer_data[3*7*i+7+3] =  0xF<<i
            vertex_buffer_data[3*7*i+7+4] =  0xF<<i
            vertex_buffer_data[3*7*i+7+5] =  math.cos(2*math.pi/self.count*i)
            vertex_buffer_data[3*7*i+7+6] =  math.sin(2*math.pi/self.count*i)

            vertex_buffer_data[3*7*i+14+0] =  math.cos(2*math.pi/self.count*(i+1))
            vertex_buffer_data[3*7*i+14+1] =  math.sin(2*math.pi/self.count*(i+1))
            vertex_buffer_data[3*7*i+14+2] =  0xF<<i
            vertex_buffer_data[3*7*i+14+3] =  0xF<<i
            vertex_buffer_data[3*7*i+14+4] =  0xF<<i
            vertex_buffer_data[3*7*i+14+5] =  math.cos(2*math.pi/self.count*(i+1))
            vertex_buffer_data[3*7*i+14+6] =  math.sin(2*math.pi/self.count*(i+1))
            
            index_buffer_data = range(0, self.count*3)
        
        attributes = [
                OGLBuffers.Attrib("inPosition", 2),
                OGLBuffers.Attrib("inColor", 3),  
                OGLBuffers.Attrib("inTexCoord", 2, 5)  ]
        self.buffers = OGLBuffers.OGLBuffers(vertex_buffer_data, 7, attributes, index_buffer_data)
        
        print(self.buffers)
    
    def init(self):
        OGLUtils.print_OGL_parameters()
        
        num_atomic = glGetIntegerv(GL_MAX_COMBINED_ATOMIC_COUNTERS)
        print("GL_MAX_COMBINED_ATOMIC_COUNTERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_VERTEX_ATOMIC_COUNTERS)
        print("GL_MAX_VERTEX_ATOMIC_COUNTERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_TESS_CONTROL_ATOMIC_COUNTERS)
        print("GL_MAX_TESS_CONTROL_ATOMIC_COUNTERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_TESS_EVALUATION_ATOMIC_COUNTERS)
        print("GL_MAX_TESS_EVALUATION_ATOMIC_COUNTERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_GEOMETRY_ATOMIC_COUNTERS)
        print("GL_MAX_GEOMETRY_ATOMIC_COUNTERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_FRAGMENT_ATOMIC_COUNTERS)
        print("GL_MAX_FRAGMENT_ATOMIC_COUNTERS  = ", num_atomic)
        
        num_atomic = glGetIntegerv(GL_MAX_COMBINED_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_COMBINED_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_VERTEX_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_VERTEX_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_TESS_CONTROL_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_TESS_CONTROL_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_TESS_EVALUATION_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_TESS_EVALUATION_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_GEOMETRY_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_GEOMETRY_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        num_atomic = glGetIntegerv(GL_MAX_FRAGMENT_ATOMIC_COUNTER_BUFFERS)
        print("GL_MAX_FRAGMENT_ATOMIC_COUNTER_BUFFERS  = ", num_atomic)
        
        for dim in range(0,3):
            val = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, dim)
            self.wg_size[dim]=val[0]
            print("GL_MAX_COMPUTE_WORK_GROUP_SIZE [", dim, "] : ", val[0])
        
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p06compute/p05atomic/drawImage")
        self.compute_shader_program = ShaderUtils.load_program_specific(None, None, None, None, None, PATH+"shaders/lvl2advanced/p06compute/p05atomic/computeImage") 
        
        self.create_buffer2()

        self.texture_viewer = OGLTexture2D.Viewer()

        self.tex_output = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_output)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, self.tex_w,
                self.tex_h, 0, GL_RGBA, GL_FLOAT, None)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        self.loc_mod_comp = glGetUniformLocation(self.compute_shader_program, "mode")
        self.loc_size_comp = glGetUniformLocation(self.compute_shader_program, "size")
        
        
        self.loc_mode = glGetUniformLocation(self.shader_program, "mode")
        self.loc_primitives = glGetUniformLocation(self.shader_program, "numPrimitives")
        self.loc_samples = glGetUniformLocation(self.shader_program, "numSamples")
        
        self.atomic_data = np.zeros(3)
        self.ac_buffer = glGenBuffers(1)
        glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, self.ac_buffer)
        glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 1, self.ac_buffer)
        glBufferData(GL_ATOMIC_COUNTER_BUFFER, self.atomic_data, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, 0)		
        
        self.query = np.zeros(2, dtype=np.int32)
        self.query = glGenQueries(len(self.query))
        
        self.textRenderer = OGLTextRenderer(self.width, self.height)
        
        self.num_primitives = 0
        self.num_samples = 0
    
    def display(self):
        wgX = int(self.count)
        wgY = int(self.count)
            
        glViewport(0, 0, self.width, self.height)
        if self.fill:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            
            
        if not self.step or self.first<2:
            glClearColor(0.1, 0.1, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                        
            self.atomic_data = np.zeros(3)
            if self.mode <= 4:
                #glDispatchCompute(256/32, 256/32, 1)
                wgX = int(self.count)
                wgY = int(self.count)
                if (wgX > self.wg_size[0]):
                    wgX = self.wg_size[0]
                if (wgY > self.wg_size[1]):
                    wgY = self.wg_size[1]
                
                #----------------------------on compute shader
                #fill texture in compute shader
                glUseProgram(self.compute_shader_program)
                glBindImageTexture (0, self.tex_output, 0, False, 0, GL_WRITE_ONLY, GL_RGBA32F)
                glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, self.ac_buffer)
                glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 1, self.ac_buffer)
                glBufferData(GL_ATOMIC_COUNTER_BUFFER, self.atomic_data, GL_DYNAMIC_DRAW)
                
                glUniform1i(self.loc_mod_comp, self.mode%4) 
                
                #glUniform2fv(locSizeComp, ToFloatArray.convert(new Vec2D(tex_w,tex_h))) 
                glUniform2fv(self.loc_size_comp, 1, np.array((wgX,wgY),dtype = np.float32))
                glDispatchCompute(wgX, wgY, 1)
                
                # make sure writing to image has finished before read
                glMemoryBarrier(GL_ALL_BARRIER_BITS | GL_SHADER_IMAGE_ACCESS_BARRIER_BIT | GL_ATOMIC_COUNTER_BARRIER_BIT)
                
                glBindImageTexture (0, self.tex_output, 0, False, 0, GL_READ_ONLY, GL_RGBA32F)
                self.texture_viewer.view(self.tex_output, -1, -1,1.5)
                
            
            else:
                if self.first<2:
                    self.create_buffer2()
                #----------------------------to FrameBuffer
                
                glUseProgram(self.shader_program) 
                
                glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, self.ac_buffer)
                glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 1, self.ac_buffer)
                
                #----------------------------Queries initialization
                # Query how many elements were drawn
                glBeginQuery(GL_PRIMITIVES_GENERATED, self.query[0])
        
                # Query how samples (pixels) were rasterized
                glBeginQuery(GL_SAMPLES_PASSED, self.query[1])
                
                
                glClearColor(0.1, 0.1, 0.1, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                glUniform1i(self.loc_mode, self.mode%4) 
                glUniform1i(self.loc_primitives, self.num_primitives) 
                glUniform1i(self.loc_samples, self.num_samples) 
                
                glBindBufferBase(GL_ATOMIC_COUNTER_BUFFER, 0, self.ac_buffer)
                glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, self.ac_buffer)
                glBufferData( GL_ATOMIC_COUNTER_BUFFER, self.atomic_data, GL_DYNAMIC_DRAW)
                
                # draw
                self.buffers.draw(GL_TRIANGLES, self.shader_program)
                
                #----------------------------Queries results
                
                glEndQuery(GL_PRIMITIVES_GENERATED)
                glEndQuery(GL_SAMPLES_PASSED)
                self.num_primitives = glGetQueryObjectiv(self.query[0], GL_QUERY_RESULT)
                self.num_samples = glGetQueryObjectiv(self.query[1], GL_QUERY_RESULT)
            
            self.first+=1
        
        text = __name__ + "[F]ill"
        if self.step:
            text += "[S]tart, "
        else:
            text += "[S]top, "

        text += ", " + "Primitives " + str(self.num_primitives)
        text += ", " + "Samples " + str(self.num_samples)
        
        if self.mode == 0:
            text += ", [m]ode: CS"
            text += ", " + "workgroup [Page up/down] " + str(wgX)+" X "+str(wgY)

        elif self.mode == 1:
            text += ", [m]ode: FS"
            text += ", " + "triangles [Page up/down] " + str(self.count)
        elif self.mode == 2:
            text += ", [m]ode: VS"
            text += ", " + "triangles [Page up/down] " + str(self.count)
        elif self.mode == 3:
            text += ", [m]ode: VS+image"
            text += ", " + "triangles [Page up/down] " + str(self.count)
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
