from transforms.Camera import Camera
from transforms import Mat4PerspRH, Mat4
from pyglutils import ShaderUtils, OGLUtils, OGLTextRenderer, OGLModelOBJ
from OpenGL.GL import *
import math
import sys
import glfw
from __main__ import PATH

class Main:
    """GLSL sample:
        Draw two different geometries with two different shader programs

        author: PGRF FIM UHK
        version: 3.0-PY
        rewrite: Matěj Kolář
        since: 11-2022
    """

    def __init__(self):
        self.width = 300
        self.height = 300
        self.mouse_button1 = False
        self.ox = 0
        self.oy = 0
        
        self.render_line = True
        self.cam = Camera()
        self.proj = Mat4PerspRH(math.pi / 4, self.height / self.width, 0.01, 1000.0)
        self.swapYZ = Mat4().from_raw_rows(
                (1, 0, 0, 0),
                (0, 0, 1, 0),
                (0, 1, 0, 0),
                (0, 0, 0, 1))
            
        
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
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        
        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(1)

        # Make the window visible
        glfw.show_window(self.window)

        OGLUtils.print_OGL_parameters()
        
        # shader files are in /shaders/ directory
        # shaders directory must be set as a source directory of the project
        # e.g. in Eclipse via main menu Project/Properties/Java Build Path/Source
                
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p02geometry/p03obj/ducky")
        #self.shader_program = ShaderUtils.loadProgram("/lvl1basic/p02geometry/p03obj/teapot")
                
        # obj files are in  /res/obj/...
        self.model = OGLModelOBJ(PATH+"res/obj/ducky.obj")
        #model = new OGLModelOBJ(PATH+"res/obj/teapot.obj")
        #model= new ModelOBJ(PATH+"res/obj/ElephantBody.obj")
        #model= new ModelOBJ(PATH+"res/obj/TexturedCube.obj")

        self.buffers = self.model.get_buffers()

        glClearColor(0.2, 0.2, 0.2, 1.0)

        glUseProgram(self.shader_program)
        
        self.loc_mat = glGetUniformLocation(self.shader_program, "mat")
        
        self.cam = self.cam.with_position((5, 5, 2.5)).with_azimuth(math.pi * 1.25).with_zenith(math.pi * -0.125)
        
        #glDisable(GL_CULL_FACE) 
        glEnable(GL_DEPTH_TEST)
        self.text_renderer = OGLTextRenderer(self.width, self.height)	
        
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_W:
                self.cam = self.cam.forward(1)
            elif key == glfw.KEY_D:
                self.cam = self.cam.right(1)
            elif key == glfw.KEY_S:
                self.cam = self.cam.backward(1)
            elif key == glfw.KEY_A:
                self.cam = self.cam.left(1)
            elif key == glfw.KEY_LEFT_CONTROL:
                self.cam = self.cam.down(1)
            elif key == glfw.KEY_LEFT_SHIFT:
                self.cam = self.cam.up(1)
            elif key == glfw.KEY_SPACE:
                self.cam = self.cam.with_first_person(not self.cam.first_person)
            elif key == glfw.KEY_R:
                self.cam = self.cam.mul_radius(0.9)
            elif key == glfw.KEY_F:
                self.cam = self.cam.mul_radius(1.1)
            elif key == glfw.KEY_P:
                self.render_line = not self.render_line
        
    def cursor_pos_callback(self, window, x, y):
        if self.mouse_button1:
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width)
            self.ox = x
            self.oy = y
        
    def mouse_button_callback(self, window, button, action, mods):
        self.mouse_button1 = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.PRESS
        
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            self.mouse_button1 = True
            self.ox, self.oy = glfw.get_cursor_pos(window)
        
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.RELEASE:
            self.mouse_button1 = False
            x,y = glfw.get_cursor_pos(window)
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width)
            self.ox = x
            self.oy = y

        

    def framebuffer_size_callback(self, window, w, h):
        if w > 0 and h > 0 and (w != self.width or h != self.height):
            self.width = w
            self.height = h
            self.proj = Mat4PerspRH(math.pi / 4, self.height / self.width, 0.01, 1000.0)
            if self.text_renderer is not None:
                self.text_renderer.resize(self.width, self.height)
 
    
    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            glEnable(GL_DEPTH_TEST)
            text = __name__ + ": [LMB] self.camera, WSAD"

            if not self.render_line:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                text += ", [p]olygon: fill"
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                text += ", [p]olygon: line"

            glViewport(0, 0, self.width, self.height)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
            
            # set the current shader to be used
            glUseProgram(self.shader_program) 
            
            glUniformMatrix4fv(self.loc_mat, 1, False, self.swapYZ.mul_mat4(self.cam.view).mul_mat4(self.proj).to_4x4array())

            # bind and draw
            self.buffers.draw(self.model.get_topology(), self.shader_program)
        
            self.text_renderer.add_str2d(3, 20, text)
            self.text_renderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
            
            
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