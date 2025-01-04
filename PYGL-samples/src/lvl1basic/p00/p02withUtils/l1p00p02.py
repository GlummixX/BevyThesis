import glfw
import sys
from OpenGL.GL import *
from pyglutils import ShaderUtils, OGLUtils
from __main__ import PATH


class Main:
    """ GLSL sample:
        Read and compile shader from files "/shader/glsl01/start.*" using ShaderUtils
        class in oglutils package 

        author PGRF FIM UHK
        version 3.0-PY
        rewrite: Matěj Kolář
        since 11-2022
    """

    def __init__(self):
        self.width = 300
        self.height = 300

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
        glfw.swap_interval(0)

        # Make the window visible
        glfw.show_window(self.window)

        OGLUtils.print_OGL_parameters()
        
        # Set the clear color
        glClearColor(0.1, 0.1, 0.1, 1.0)

        self.shader_program = ShaderUtils.load_program_specific(PATH+"shaders/lvl1basic/p01start/start.vert",
                PATH+"shaders/lvl1basic/p01start/start.frag") 
        
        #shorter version of loading shader program
        #self.shader_program = ShaderUtils.loadProgram("/lvl1basic/p01start/start") 
        
        #for older GLSL version 
        #self.shader_program = ShaderUtils.loadProgram("/lvl1basic/p01start/startForOlderGLSL")
        
        # Shader program set
        glUseProgram(self.shader_program)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
    
    def framebuffer_size_callback(self, window, width, height):
        if width > 0 and height > 0 and (self.width != width or self.height != height):
            self.width = width
            self.height = height
    
    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            
            glViewport(0, 0, self.width, self.height)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer

            # Rendering triangle by fixed pipeline
            glBegin(GL_TRIANGLES)
            glColor3f(1, 0, 0)
            glVertex2f(-1, -1)
            glColor3f(0, 1, 0)
            glVertex2f(1, 0)
            glColor3f(0, 0, 1)
            glVertex2f(0, 1)
            glEnd()
            
            glfw.swap_buffers(self.window) # swap the color buffers

            # Poll for window events. The key callback above will only be
            # invoked during this call.
            glfw.poll_events()

    def run(self):
        self.loop()
        if bool(glDeleteProgram):
            glDeleteProgram(self.shader_program) 
        glfw.destroy_window(self.window)
        glfw.terminate()
        glfw.set_error_callback(None)