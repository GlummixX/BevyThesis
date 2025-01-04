import glfw
import sys
from pyglutils import OGLUtils, ShaderUtils
from OpenGL.GL import *
from __main__ import PATH
import numpy as np

class Main:
    """GLSL sample:
        Sending minimal geometry to GPU
        Requires LWJGL3
        
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

        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(0)

        # Make the window visible
        glfw.show_window(self.window)

        OGLUtils.print_OGL_parameters()
        
        # Set the clear color
        glClearColor(0.1, 0.1, 0.1, 1.0)

        self.create_buffers()
        
        self.shader_program = ShaderUtils.load_program_specific(PATH+"shaders/lvl1basic/p01start/start.vert",
                PATH+"shaders/lvl1basic/p01start/start.frag") 
        
        # Shader program set
        glUseProgram(self.shader_program)


    def key_callback (self, window, key, scancode, action, mods):
            if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
                glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
    
    def create_buffers(self):
        # create and fill vertex buffer data
        vertex_buffer_data = [
                -1, -1, 
                1, 0, 
                0, 1 
            ]
        # create buffer required for sending data to a native library
        vertex_buffer_buffer = np.asarray(vertex_buffer_data, dtype=np.float32)
        
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertex_buffer_buffer, GL_STATIC_DRAW)

        # create and fill index buffer data (element buffer in OpenGL terminology)
        index_buffer_data = [0, 1, 2]
        
        # create buffer required for sending data to a native library
        index_buffer_buffer = np.asarray(index_buffer_data,dtype=np.uint16)

        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_buffer_buffer, GL_STATIC_DRAW)

    def bind_buffers(self):
        # internal OpenGL ID of a vertex shader input variable
        loc_position = glGetAttribLocation(self.shader_program, "inPosition") 

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        # bind the shader variable to specific part of vertex data (attribute)
        # - describe how many components of which type correspond to it in the
        # data, how large is one vertex (its stride in bytes) and at which byte
        # of the vertex the first component starts
        # 2 components, of type float, do not normalize (convert to [0,1]),
        # vertex of 8 bytes, start at the beginning (byte 0)
        glVertexAttribPointer(loc_position, 2, GL_FLOAT, False, 8, ctypes.c_void_p(0))
        glEnableVertexAttribArray(loc_position)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer

            # set the current shader to be used, could have been done only once (in
            # init) in this sample (only one shader used)
            glUseProgram(self.shader_program) 
            # to use the default shader of the "fixed pipeline", call
            # glUseProgram(0)

            # bind the vertex and index buffer to shader, could have been done only
            # once (in init) in this sample (only one geometry used)
            self.bind_buffers()
            # draw
            glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_SHORT, ctypes.c_void_p(0))

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