import math
from abc import ABC, abstractmethod
from pyglutils import OGLUtils, OGLTextRenderer
from OpenGL.GL import *
import glfw

class Abstract_renderer():
    """ author PGRF FIM UHK
        version 2.0-PY
        rewrite: Matěj Kolář
        since 10-2022
    """
    passing = 0
    width = 300
    height = 300
    textRenderer = None
    
    @abstractmethod
    def init(self):
        OGLUtils.print_OGL_parameters()
        #OGLUtils.print_lwj_lparameters()
        #OGLUtils.print_jav_aparameters()
        OGLUtils.shader_check()
        # Set the clear color
        glClearColor(0.0, 0.0, 0.0, 0.0)
        self.textRenderer = OGLTextRenderer(self.width, self.height)
        
    @abstractmethod
    def display(self):
        glViewport(0, 0, self.width, self.height)
        text = __name__ + ": look at console and try keys, mouse, wheel and window interaction"
        
        self.passing += 1
        # Set the clear color
        glClearColor(math.sin(self.passing/100)/2+0.5, math.cos(self.passing/200)/2+0.5,math.sin(self.passing/300)/2+0.5, 0.0)
        # clear the framebuffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        #create and draw text
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(3, 50, f"pass{self.passing}")
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")

    @abstractmethod
    def key_callback(self, window, key, scancode, action, mods):
        if (key == glfw.KEY_ESCAPE and action == glfw.RELEASE):
            # We will detect this in our rendering loop
            glfw.set_window_should_close(window, True)
        if (action == glfw.RELEASE):
            print("Key release " , key)
        if (action == glfw.PRESS):
            print("Key pressed " , key)


    
    @abstractmethod
    def ws_callback(self, window, w, h):
        if w > 0 and h > 0:
            self.width = w
            self.height = h
            print("Windows resize to [" , w , ", " , h , "]")
            if (self.textRenderer is not None):
                self.textRenderer.resize(self.width, self.height)

    @abstractmethod
    def mb_callback(self, window, button, action, mods):
        #mouseButton1 = glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_1) == GLFW_PRESS
        x, y = glfw.get_cursor_pos(window)

        if button==glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            print("Mouse button 1 is pressed at coursor position [" , x , ", " , y , "]")
        
        if (button==glfw.MOUSE_BUTTON_1 and action == glfw.RELEASE):
            print("Mouse button 1 is released at coursor position [" , x , ", " , y , "]")

    
    @abstractmethod
    def cp_callback(self, window, x, y):
        print("Coursor position [" , x , ", " , y , "]")

    @abstractmethod
    def scroll_callback(self, window, dx, dy):
        print("Mouse whell velocity " , dy)
    
    @abstractmethod
    def dispose(self):
        pass
