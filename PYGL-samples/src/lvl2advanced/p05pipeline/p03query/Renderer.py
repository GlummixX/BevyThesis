from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
from pyglutils import OGLBuffers, ShaderUtils, OGLUtils, OGLTextRenderer
from OpenGL.GL import *
import numpy as np
import glfw
from __main__ import PATH

class Renderer(Abstract_renderer):
    """author PGRF FIM UHK
        version 2.0-PY
        rewrite Matěj Kolář
        since 2019-09-02
    """

    def __init__(self):
        self.mode = 0


    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_E:
                self.mode += 1
    
    def ws_callback(self, window, w, h):
        if (w > 0 and h > 0 and 
                (w != self.width or h != self.height)):
            self.width = w
            self.height = h
            if self.textRenderer is not None:
                self.textRenderer.resize(self.width, self.height)
        
    def create_input_buffer(self):
        indexBufferData = [0, 1, 2, 3]
    
        vertexBufferDataPos1 = [
                -.5, -.1,  0.0, 1.0, 0.1,
                -.3, .5,  0.0, 1.0, 1.0,
                .2, -.4,  0.0, 0.5, 0.5,
                .3, .8,  0.0, 0.1, 1.0]
            
        attributesPos = [
                OGLBuffers.Attrib("inPosition", 2),
                OGLBuffers.Attrib("inColor", 3)]
        self.buffers = OGLBuffers.OGLBuffers(vertexBufferDataPos1, None, attributesPos, indexBufferData)
    
    def init(self):
        OGLUtils.print_OGL_parameters()
        
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p03query/feedbackDraw")
        
        self.create_input_buffer()
        self.query = np.zeros(4, dtype=np.int32)
        self.textRenderer = OGLTextRenderer(self.width, self.height)
    
    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        self.query = glGenQueries(len(self.query))

        # Query how many elements were drawn
        glBeginQuery(GL_PRIMITIVES_GENERATED, self.query[0])

        # Query how samples (pixels) were rasterized
        glBeginQuery(GL_SAMPLES_PASSED, self.query[1])
                    
        # Query time counter of rendering
        glBeginQuery(GL_TIME_ELAPSED, self.query[2])

        glPointSize(5)
        glUseProgram(self.shader_program)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        text = __name__
        
        self.mode = self.mode%6
        if self.mode == 0: 
            text += ": " + "[E]lements GL_POINTS" 
            self.buffers.draw(GL_POINTS, self.shader_program)
        elif self.mode == 1: 
            text += ": " + "[E]lements GL_LINES" 
            self.buffers.draw(GL_LINES, self.shader_program)
        elif self.mode == 2: 
            text += ": " + "[E]lements GL_LINE_LOOP" 
            self.buffers.draw(GL_LINE_LOOP, self.shader_program)
        elif self.mode == 3: 
            text += ": " + "[E]lements GL_TRIANGLES" 
            self.buffers.draw(GL_TRIANGLES, self.shader_program)
        elif self.mode == 4: 
            text += ": " + "[E]lements GL_TRIANGLE_STRIP" 
            self.buffers.draw(GL_TRIANGLE_STRIP, self.shader_program)
        elif self.mode == 5: 
            text += ": " + "[E]lements NONE"
        
        glEndQuery(GL_PRIMITIVES_GENERATED)
        result = glGetQueryObjectiv(self.query[0], GL_QUERY_RESULT)

        text += ", " + "Primitives " + str(result)
        
        glEndQuery(GL_SAMPLES_PASSED)
        result = glGetQueryObjectiv(self.query[1], GL_QUERY_RESULT)

        text += ", " + "Samples " + str(result)
        
        glEndQuery(GL_TIME_ELAPSED)
        result = glGetQueryObjectiv(self.query[2], GL_QUERY_RESULT)

        text += ", " + "Pass time " + str(round(result/1e6,2))+"ms"
        
        glQueryCounter(self.query[3], GL_TIMESTAMP)
        result_long = glGetQueryObjecti64v(self.query[3], GL_QUERY_RESULT, np.zeros(1,dtype=np.int64))

        glDeleteQueries(self.query)
        
        text += ", " + "Time stamp " + str(round(result_long/1e9,2)) +"s"
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")