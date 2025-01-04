from transforms.Camera import Camera
from transforms import Mat4PerspRH
from pyglutils import ShaderUtils, OGLUtils, OGLTextRenderer, OGLBuffers
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

        self.render_line = False
        self.mode = 0

        self.cam = Camera()
        self.proj = Mat4PerspRH(math.pi / 4, 1, 0.01, 1000.0)

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
        
        glClearColor(0.2, 0.2, 0.2, 1.0)

        self.create_buffers()
        
        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p02geometry/p02strip/simple")
        
        glUseProgram(self.shader_program)
        
        self.loc_mat = glGetUniformLocation(self.shader_program, "mat")
        
        self.cam = self.cam.with_position((5, 5, 2.5)).with_azimuth(math.pi * 1.25).with_zenith(math.pi * -0.125)
        
        glDisable(GL_CULL_FACE) 
        glFrontFace(GL_CCW)
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
            elif key == glfw.KEY_M:
                self.mode+=1
        
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
            x, y = glfw.get_cursor_pos(window)
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

    def create_buffers(self):
        strip = [
                # first triangle
                1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, -1, 1, 1, 0, 0, 0, -1,
                # second triangle
                0, 0, 0, 0, -1, 0, 1, 1, 0, 0, -1, 0, 0, 1, 0, 0, -1, 0,
                # 3st triangle
                1, 1, 0, -1, 0, 0, 0, 1, 0, -1, 0, 0, 1, 2, 0, -1, 0, 0,
                # 4th triangle
                0, 1, 0, 0, 1, 0, 1, 2, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0,
                # 5th triangle
                1, 2, 0, 0, 0, 1, 0, 2, 0, 0, 0, 1, 1, 3, 0, 0, 0, 1,
                # 6th triangle
                0, 2, 0, 1, 0, 0, 1, 3, 0, 1, 0, 0, 0, 3, 0, 1, 1, 1,
            ]

        attributes = [
            OGLBuffers.Attrib("inPosition", 3),
            OGLBuffers.Attrib("inNormal", 3) ]

        # create geometry without index buffer as the triangle list
        self.buffers = OGLBuffers.OGLBuffers(strip, None, attributes)

        index_buffer_data = [None]*9
        for i in range(0,9,3):
            index_buffer_data[i] = 2 * i
            index_buffer_data[i + 1] = 2 * i + 1
            index_buffer_data[i + 2] = 2 * i + 2
        # create geometry with index buffer as the triangle list [0, 1, 2, 6, 7, 8, 12, 13, 14]
        self.buffers2 = OGLBuffers.OGLBuffers(strip, None, attributes, index_buffer_data)

        index_buffer_data2 = [ 0, 1, 2, 5, 8, 11, 14, 17 ]
        # create geometry with index buffer as the triangle strip
        self.buffers3 = OGLBuffers.OGLBuffers(strip, None, attributes, index_buffer_data2)

        index_buffer_data3 = [ 0, 1, 2, 5, 65535, 12, 13, 14, 17 ]
        # create geometry with index buffer as the triangle strip with restart index
        self.buffers4 = OGLBuffers.OGLBuffers(strip, None, attributes, index_buffer_data3)
        print("buffers \n " + self.buffers.to_string())
        print("buffers \n " + self.buffers2.to_string())
        print("buffers \n " + self.buffers3.to_string())
        print("buffers \n " + self.buffers4.to_string())

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):

            glViewport(0, 0, self.width, self.height)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the
                                                                # framebuffer

            # set the current shader to be used
            glUseProgram(self.shader_program)

            glUniformMatrix4fv(self.loc_mat, 1, False, self.cam.view.mul_mat4(self.proj).to_4x4array())

            text = __name__ + ": [LMB] self.camera, WSAD"

            if not self.render_line:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                text += ", [p]olygon: fill"
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                text += ", [p]olygon: line"

            # bind and draw
            self.mode = self.mode % 11
            if self.mode == 0:
                text += ", [m]ode: all triangles of triangle list, without index buffer"
                self.buffers.draw(GL_TRIANGLES, self.shader_program)
            elif self.mode == 1:
                text += ", [m]ode: first 3 triangles of triangle list, without index buffer"
                # number of vertices
                self.buffers.draw(GL_TRIANGLES, self.shader_program, 9)
            elif self.mode == 2:
                text += ", [m]ode: 3rd, 4th and 5th triangles of triangle list, without index buffer"
                # number of vertices, index of the first vertex
                self.buffers.draw(GL_TRIANGLES, self.shader_program, 9, 6)
            elif self.mode == 3:
                text += ", [m]ode: odd triangles of triangle list, with defined index buffer"
                self.buffers2.draw(GL_TRIANGLES, self.shader_program)
            elif self.mode == 4:
                text += ", [m]ode: 1st and 2nd odd triangles of triangle list, with defined index buffer"
                # number of vertices
                self.buffers2.draw(GL_TRIANGLES, self.shader_program, 6)
            elif self.mode == 5:
                text += ", [m]ode: 2nd and 3rd odd triangles of triangle list, with defined index buffer"
                # number of vertices, index of the first vertex
                self.buffers2.draw(GL_TRIANGLES, self.shader_program, 6, 3)
            elif self.mode == 6:
                text += ", [m]ode: all triangles of triangle strip, with defined index buffer"
                self.buffers3.draw(GL_TRIANGLE_STRIP, self.shader_program)
            elif self.mode == 7:
                text += ", [m]ode: first 3 triangles of triangle strip, with defined index buffer"
                # number of vertices
                self.buffers3.draw(GL_TRIANGLE_STRIP, self.shader_program, 5)
            elif self.mode == 8:
                text += ", [m]ode: 3rd and 4th triangles of triangle strip, with defined index buffer and range"
                # number of vertices, index of the first vertex
                self.buffers3.draw(GL_TRIANGLE_STRIP, self.shader_program, 4, 2)
            elif self.mode == 9:
                text += ", [m]ode: 1st-2nd and 5th-6th triangles of triangle strip, with defined index buffer and primitive restart index"
                # number of vertices, index of the first vertex
                glEnable(GL_PRIMITIVE_RESTART)
                glPrimitiveRestartIndex(65535)
                self.buffers4.draw(GL_TRIANGLE_STRIP, self.shader_program)
                glDisable(GL_PRIMITIVE_RESTART)
            elif self.mode == 10:
                text += ", [m]ode: 1st and 4-6 triangles of triangle strip, with defined index buffer, primitive restart index and range"
                # number of vertices, index of the first vertex
                glEnable(GL_PRIMITIVE_RESTART)
                glPrimitiveRestartIndex(65535)
                self.buffers4.draw(GL_TRIANGLE_STRIP, self.shader_program,8,1)
                glDisable(GL_PRIMITIVE_RESTART)
            
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

