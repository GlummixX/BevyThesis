import glfw
import sys
from OpenGL.GL import *

class Main:
    """ GLSL sample:
        Read and compile shader from string 
        
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

        print("OpenGL version ", glGetString(GL_VERSION))
        print("OpenGL vendor ", glGetString(GL_VENDOR))
        print("OpenGL renderer ", glGetString(GL_RENDERER))
        print("OpenGL extension ", glGetString(GL_EXTENSIONS))
        
        # Set the clear color
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Create all needed GL resources
        self.create_shaders()
        
        # Fixed pipeline set
        glUseProgram(self.shader_program)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
    
    def framebuffer_size_callback(self, window, width, height):
        if width > 0 and height > 0 and (self.width != width or self.height != height):
            self.width = width
            self.height = height
    
    def create_shaders(self):
        shader_vert_src = [
            "#version 150\n",
            "in vec2 inPosition;", # input from the vertex buffer
            "void main() {", 
            "	vec2 position = inPosition;",
            "   position.x += 0.1;",
            " 	gl_Position = vec4(position, 0.0, 1.0);",
            "}"
            ]
        # gl_Position - built-in vertex shader output variable containing
        # vertex position before w-clipping and dehomogenization, must be
        # filled

        shader_frag_src = [ 
            "#version 150\n",
            "out vec4 outColor;", # output from the fragment shader
            "void main() {",
            " 	outColor = vec4(0.5,0.1,0.8, 1.0);",
            "}"
            ]

        # vertex shader
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, shader_vert_src)
        glCompileShader(vs)
        compiled = glGetShaderiv(vs, GL_COMPILE_STATUS)
        shaderLog = glGetShaderInfoLog(vs)
        if len(shaderLog) > 0:
            print(shaderLog)
        if compiled == 0:
            print("Could not compile VS shader")
        
        # fragment shader
        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, shader_frag_src)
        glCompileShader(fs)
        compiled = glGetShaderiv(fs, GL_COMPILE_STATUS)
        shaderLog = glGetShaderInfoLog(fs)
        if len(shaderLog) > 0:
            print(shaderLog)
        if compiled == 0:
            print("Could not compile FS shader")
        
        # link program
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, vs)
        glAttachShader(self.shader_program, fs)
        glLinkProgram(self.shader_program)
        linked = glGetProgramiv(self.shader_program, GL_LINK_STATUS)
        programLog = glGetProgramInfoLog(self.shader_program)
        if len(programLog) > 0:
            print(programLog)
        if linked == 0:
            print("Could not link program")
        
        if vs > 0: glDetachShader(self.shader_program, vs)
        if fs > 0: glDetachShader(self.shader_program, fs)
        if vs > 0: glDeleteShader(vs)
        if fs > 0: glDeleteShader(fs)
    
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