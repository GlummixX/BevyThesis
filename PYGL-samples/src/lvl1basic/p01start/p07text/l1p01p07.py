import glfw
import sys
from pyglutils import OGLUtils, ShaderUtils, OGLTextRenderer, OGLBuffers
from OpenGL.GL import *
from __main__ import PATH
import math
from PIL import ImageFont
import time

class Main:
    """GLSL sample:
        Print texts and draw two different geometries with two different shader programs using depth buffer

        author: PGRF FIM UHK
        version: 3.0-PY
        rewrite: Matěj Kolář
        since: 11-2022
    """
    def __init__(self):
        self.width = 300
        self.height = 300
        self.frame = 0
        self.depth_test = False
        self.oldFPSmils = 0

        # Initialize GLFW. Most GLFW functions will not work before doing this.
        if not glfw.init():
            print("Unable to initialize GLFW")
            sys.exit(1)

        # Configure GLFW
        glfw.default_window_hints() # optional, the current window hints are already the default
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE) # the window will stay hidden after creation
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE) # the window will be resizable

        # Create the window
        self.window = glfw.create_window(self.width, self.height, "Hello World!", None, None)
        if self.window is None:
            print("Failed to create the GLFW window")
            sys.exit(1)

        # Setup a key callback. It will be called every time a key is pressed, repeated or released.
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)

        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(1)

        # Make the window visible
        glfw.show_window(self.window)
        
        OGLUtils.print_OGL_parameters()
        
        # Set the clear color
        glClearColor(0.1, 0.1, 0.1, 1.0)

        self.create_buffers()
        
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p01start/p06depthbuffer/start")
        self.shader_program2 = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p01start/p06depthbuffer/start2")
        
        # Shader program set
        glUseProgram(self.shader_program)
        
        # internal OpenGL ID of a shader uniform (constant during one draw call
        # - constant value for all processed vertices or pixels) variable
        self.loc_time = glGetUniformLocation(self.shader_program, "time")
        self.loc_time2 = glGetUniformLocation(self.shader_program2, "time")

        self.text_renderer = OGLTextRenderer(self.width, self.height)
        self.text_renderer2 = OGLTextRenderer(self.width, self.height, ImageFont.truetype("NotoSerif-Bold.ttf", 20, 0))
        self.text_renderer3 = OGLTextRenderer(self.width, self.height)
        self.text_renderer3.color = (0,0,255,255)
        self.text_renderer3.bgColor = (200,200,200,255)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if key == glfw.KEY_D and action == glfw.RELEASE:
            self.depth_test = not self.depth_test
            print("Depth test is ", "on" if self.depth_test else "off")

    def framebuffer_size_callback(self, window, width, height):
            if width > 0 and height > 0 and (self.width != width or self.height != height):
                self.width = width
                self.height = height
                if self.text_renderer is not None:
                    self.text_renderer.resize(width, height)
                    self.text_renderer2 = OGLTextRenderer(width, height, ImageFont.truetype("NotoSerif-Bold.ttf", 20, 0))
                    self.text_renderer3.resize(width, height)
    
    def create_buffers(self):
        vertex_buffer_data = [
            -1, -1, 	0.7, 0, 0, 
             1,  0,		0, 0.7, 0,
             0,  1,		0, 0, 0.7 
        ]
        index_buffer_data = [ 0, 1, 2 ]

        # vertex binding description, concise version
        attributes = [
                OGLBuffers.Attrib("inPosition", 2), # 2 floats
                OGLBuffers.Attrib("inColor", 3) # 3 floats
            ]
        self.buffers = OGLBuffers.OGLBuffers(vertex_buffer_data, None, attributes, index_buffer_data)
        
        vertex_buffer_data_pos = [
                -1, 1, 
                0.5, 0,
                -0.5, -1 
            ]
        vertex_buffer_data_col = [
                0, 1, 1, 
                1, 0, 1,
                1, 1, 1 
            ]
        attributes_pos = [OGLBuffers.Attrib("inPosition", 2),]
        attributes_col = [OGLBuffers.Attrib("inColor", 3)]
        
        self.buffers2 = OGLBuffers.OGLBuffers(vertex_buffer_data_pos, None, attributes_pos, index_buffer_data)
        self.buffers2.add_vertex_buffer(vertex_buffer_data_col, attributes_col)

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):

            # fps calculation every ten frames
            if self.frame%10 == 0 :
                mils = time.perf_counter()*1000
                fps = 10000 / (mils - self.oldFPSmils + 1)
                self.oldFPSmils = mils

            text = __name__
            if self.depth_test:
                #enable depth test
                glEnable(GL_DEPTH_TEST)
                text += ": [D]epth test"
            else:
                #disable depth test
                glDisable(GL_DEPTH_TEST)
                text += ": [d]epth test"
            	
            
            glViewport(0, 0, self.width, self.height)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
            self.frame += 1
            
            # set the current shader to be used
            glUseProgram(self.shader_program) 
            glUniform1f(self.loc_time, self.frame/100) # correct shader must be set before this
            
            # bind and draw
            self.buffers.draw(GL_TRIANGLES, self.shader_program)
            
            # set the current shader to be used
            glUseProgram(self.shader_program2) 
            glUniform1f(self.loc_time2, self.frame/100) # correct shader must be set before this
            
            # bind and draw
            self.buffers2.draw(GL_TRIANGLES, self.shader_program2)
            
            #create and draw text
            self.text_renderer2.color = (255, 128, 0, 255)
            self.text_renderer2.bgColor = (255, 255, 255, 0)
            for i in range(1,11):
                self.text_renderer2.rotationAngle = math.pi*2.*i/10
                self.text_renderer2.scale = 0.2 * (1 + i)
                self.text_renderer2.add_str2d(self.width / 2, self.height / 2, "HelloWorld")
        
            self.text_renderer3.add_str2d(3, 60, "áčéěíňůúřšťýž")
            self.text_renderer3.add_str2d(3, 40, "ABCČDĎEÉĚFGHIÍJKLĽMNŇOÓPQRŘSŠTŤUÚVWXYÝZŽ")
            self.text_renderer3.add_str2d(3, self.height-3, "0123456789")
            
            self.text_renderer.add_str2d(3, self.height-23, f"frame: {self.frame} fps: {round(fps,1)}")

            self.text_renderer.add_str2d(3, 20, text)
            self.text_renderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
            
            # Poll for window events. The key callback above will only be
            # invoked during this call.
            glfw.swap_buffers(self.window) # swap the color buffers
            glfw.poll_events()

    def run(self):
        self.loop()
        if bool(glDeleteProgram):
            glDeleteProgram(self.shader_program) 
        glfw.destroy_window(self.window)
        glfw.terminate()
        glfw.set_error_callback(None)