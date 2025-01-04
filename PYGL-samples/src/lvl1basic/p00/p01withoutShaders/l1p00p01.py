import glfw
import sys
from OpenGL.GL import *


class Main:
    """GLSL sample:
        Rendering without shaders, using fixed pipeline

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

        print("OpenGL version ", glGetString(GL_VERSION))
        print("OpenGL vendor ", glGetString(GL_VENDOR))
        print("OpenGL renderer ", glGetString(GL_RENDERER))
        print("OpenGL extension ", glGetString(GL_EXTENSIONS))
        
        # Set the clear color
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # Fixed pipeline set
        glUseProgram(0)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
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
        glfw.destroy_window(self.window)
        glfw.terminate()
        glfw.set_error_callback(None)