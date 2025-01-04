from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import sys
import math
from pyglutils import ShaderUtils, OGLTexture2D, OGLBuffers, OGLTextRenderer
from transforms import Mat4Scale, Mat4PerspRH, Camera
from __main__ import PATH


# GLSL sample
# Draw two different geometries with two different shader programs
# 
# author PGRF FIM UHK 
# PY rewrite: Kolář Matěj
# version 3.0-PY
# since 2019-07-11

class Main:
    
    #OGLBuffers buffers 
    #OGLTextRenderer textRenderer 
    #OGLTexture2D.Viewer textureViewer  
    #OGLTexture2D texture 
    
    def __init__(self):
        self.width = 300
        self.height = 300 
        self.mouseButton1 = False 
        self.window = None
        self.ox = 0
        self.oy = 0
        
        self.cam = Camera((5, 5, 2.5), math.pi * 1.25, math.pi * -0.125)
        self.proj = Mat4PerspRH(math.pi / 4, 1, 0.1, 100.0)
    
        # Initialize GLFW. Most GLFW functions will not work before doing self.
        if not glfw.init():
            sys.exit(1)

        # Configure GLFW
        glfw.default_window_hints()# optional, the current window hints are already the default
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE) # the window will stay hidden after creation
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)# the window will be resizable

        # Create the window
        self.window = glfw.create_window(self.width, self.height, "Hello World!", None, None) 
        if self.window == None:
            print("Failed to create the GLFW window") 
            sys.exit(1)
                    
        # Setup a key callback. It will be called every time a key is pressed, repeated or released.
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        
        # Get the thread stackand push a new frame
        #try ( MemoryStack stack = stackPush() ) {
        #    IntBuffer pWidth = stack.mallocInt(1)  # int*
        #    IntBuffer pHeight = stack.mallocInt(1)  # int*

           # Get the window size passed to glfwCreateWindow
        #    glfwGetWindowSize(window, pWidth, pHeight) 

            # Get the resolution of the primary monitor
        #    GLFWVidMode vidmode = glfwGetVideoMode(glfwGetPrimaryMonitor()) 

            # Center the window
        #     glfwSetWindowPos(
        #        window, 
        #        (vidmode.width() - pWidth.get(0)) / 2, 
        #        (vidmode.height() - pHeight.get(0)) / 2
        #    ) 
        # }# the stack frame is popped automatically

        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(1)
        # Make the window visible
        glfw.show_window(self.window)
        
        glClearColor(0.2, 0.2, 0.2, 1.0) 

        self.create_buffers() 
        self.shaderProgram = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p04target/p01intro/texture") 
        
        glUseProgram(self.shaderProgram) 
        
        self.locMat = glGetUniformLocation(self.shaderProgram, "mat") 
        
        try:
            self.texture = OGLTexture2D().from_file(PATH+"res/textures/mosaic.jpg") 
        except Exception as e: 
            print(e)
        
        glDisable(GL_CULL_FACE) 
        glEnable(GL_DEPTH_TEST) 
        self.create_target(200, 200) 
        
        self.textureViewer = OGLTexture2D.Viewer() 
        
        self.textRenderer = OGLTextRenderer(self.width, self.height)     
    

    def cursor_pos_callback(self, window, x, y):
        if self.mouseButton1:
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width)
            self.ox = x 
            self.oy = y 
        
    def mouse_button_callback(self, window, button, action, mods):
        self.mouseButton1 = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.PRESS
        if button == glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            self.mouseButton1 = True 
            x, y = glfw.get_cursor_pos(window) 
            self.ox = x
            self.oy = y
       
        if button == glfw.MOUSE_BUTTON_1 and action == glfw.RELEASE:
            self.mouseButton1 = False 
            x, y = glfw.get_cursor_pos(window)  
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width) 
            self.ox = x 
            self.oy = y 

        
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(self.window, True)# We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_W:
                self.cam = self.cam.forward(1) 
            elif key == glfw.KEY_D:
                self.cam = self.cam.right(1)  
            elif key == glfw.KEY_S:
                self.cam = self.cam.forward(-1)  
            elif key == glfw.KEY_A:
               self.cam = self.cam.right(-1)  
            elif key == glfw.KEY_LEFT_CONTROL:
               self.cam = self.cam.up(-1)  
            elif key == glfw.KEY_LEFT_SHIFT:
               self.cam = self.cam.up(1)  
            elif key == glfw.KEY_SPACE:
               self.cam = self.cam.with_first_person(not self.cam.first_person)  
            elif key == glfw.KEY_R:
               self.cam = self.cam.mul_radius(0.9)  
            elif key == glfw.KEY_F:
               self.cam = self.cam.mul_radius(1.1)  
                    
    def framebuffer_size_callback(self, window, w, h):
        if w > 0 and h > 0 and (w != self.width or h != self.height):
            self.width = w
            self.height = h 
            self.proj = Mat4PerspRH(math.pi / 4, 1, 0.1, 100.0)
            if self.textRenderer is not None:
                self.textRenderer.resize(self.width, self.height) 


    def create_target(self, targetWidth, targetHeight):
        self.colorBuffer = glGenTextures(1) 
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, targetWidth, targetHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, None) 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR) 
        
        
        self.depthBuffer = glGenTextures(1) 
        glBindTexture(GL_TEXTURE_2D, self.depthBuffer) 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, targetWidth, targetHeight, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None) 
        glBindTexture(GL_TEXTURE_2D, 0) 
        
        self.frameBuffer = glGenFramebuffers(1) 
        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBuffer) 
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                GL_TEXTURE_2D, self.colorBuffer, 0) 
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, 
                GL_TEXTURE_2D, self.depthBuffer, 0) 
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
            print("There is a problem with the FBO") 
         
    
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBuffer) 
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthBuffer, 0) 
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                GL_TEXTURE_2D, self.colorBuffer, 0) 
        
        fboStatus = glCheckFramebufferStatus(GL_FRAMEBUFFER) 
        if (fboStatus != GL_FRAMEBUFFER_COMPLETE):
            print("Could not create FBO: " + fboStatus) 
     
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0) 
            

    def bind_color_buffer_as_texture(self):
        glActiveTexture(GL_TEXTURE0) 
        glBindTexture(GL_TEXTURE_2D, self.colorBuffer) 
        locTexture = glGetUniformLocation(self.shaderProgram, "textureID") 
        glUniform1i(locTexture, 0) 
        

    def bind_depth_buffer_as_texture(self):
        glActiveTexture(GL_TEXTURE0) 
        glBindTexture(GL_TEXTURE_2D, self.depthBuffer) 
        locTexture = glGetUniformLocation(self.shaderProgram, "textureID") 
        glUniform1i(locTexture, 0) 
   

    def create_buffers(self):
        # vertices are not shared among triangles (and thus faces) so each face
        # can have a correct normal in all vertices
        # also because of this, the vertices can be directly drawn as GL_TRIANGLES
        # (threeand three vertices form one face) 
        # triangles defined in index buffer
        cube = [
                # bottom (z-) face
                1, 0, 0,    0, 0, -1,     1, 0, 
                0, 0, 0,    0, 0, -1,    0, 0, 
                1, 1, 0,    0, 0, -1,    1, 1, 
                0, 1, 0,    0, 0, -1,    0, 1, 
                # top (z+) face
                1, 0, 1,    0, 0, 1,    1, 0, 
                0, 0, 1,    0, 0, 1,    0, 0, 
                1, 1, 1,    0, 0, 1,    1, 1, 
                0, 1, 1,    0, 0, 1,    0, 1, 
                # x+ face
                1, 1, 0,    1, 0, 0,    1, 0, 
                1, 0, 0,    1, 0, 0,    0, 0, 
                1, 1, 1,    1, 0, 0,    1, 1, 
                1, 0, 1,    1, 0, 0,    0, 1, 
                # x- face
                0, 1, 0,    -1, 0, 0,    1, 0, 
                0, 0, 0,    -1, 0, 0,    0, 0, 
                0, 1, 1,    -1, 0, 0,    1, 1, 
                0, 0, 1,    -1, 0, 0,    0, 1, 
                # y+ face
                1, 1, 0,    0, 1, 0,    1, 0, 
                0, 1, 0,    0, 1, 0,    0, 0, 
                1, 1, 1,    0, 1, 0,    1, 1, 
                0, 1, 1,    0, 1, 0,    0, 1, 
                # y- face
                1, 0, 0,    0, -1, 0,    1, 0, 
                0, 0, 0,    0, -1, 0,    0, 0, 
                1, 0, 1,    0, -1, 0,    1, 1, 
                0, 0, 1,    0, -1, 0,    0, 1
        ]

        indexBufferData = [None]*36
        for i in range(0, 6):
            indexBufferData[i*6] = i*4 
            indexBufferData[i*6 + 1] = i*4 + 1 
            indexBufferData[i*6 + 2] = i*4 + 2 
            indexBufferData[i*6 + 3] = i*4 + 1 
            indexBufferData[i*6 + 4] = i*4 + 2 
            indexBufferData[i*6 + 5] = i*4 + 3 
                
        attributes = [
                OGLBuffers.Attrib("inPosition", 3), 
                OGLBuffers.Attrib("inNormal", 3), 
                OGLBuffers.Attrib("inTextureCoordinates", 2)
                ]

        self.buffers = OGLBuffers.OGLBuffers(cube, None, attributes, indexBufferData) 

        print(self.buffers.to_string()) 

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            glEnable(GL_DEPTH_TEST)
            # set the current shader to be used
            glUseProgram(self.shaderProgram)  
            
            # set our render target (texture)
            glBindFramebuffer(GL_FRAMEBUFFER, self.frameBuffer) 
            glViewport(0, 0, 200, 200) 
            
            glClearColor(0.7, 1.0, 1.0, 1.0) 
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the framebuffer
            
            self.texture.bind_slot(self.shaderProgram, "textureID", 0) 
            
            scale = Mat4Scale(self.width / self.height, 1, 1)
            glUniformMatrix4fv(self.locMat, 1, False, self.cam.view.mul_mat4(self.proj).mul_mat4(scale).to_4x4array())
            
            # bindand draw
            self.buffers.draw(GL_TRIANGLES, self.shaderProgram) 
            
            # set the default render target (screen)
            glBindFramebuffer(GL_FRAMEBUFFER, 0) 
            glViewport(0, 0, self.width, self.height) 

            glClearColor(0.1, 0.1, 0.1, 1.0) 
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the framebuffer
            
            # use the result of the previous draw as a texture for the next
            self.bind_color_buffer_as_texture() 
            #bindDepthBufferAsTexture() 
            
            glUniformMatrix4fv(self.locMat, 1, False, self.cam.view.mul_mat4(self.proj).to_4x4array())
            
            self.buffers.draw(GL_TRIANGLES, self.shaderProgram) 
            
            self.textureViewer.view(self.depthBuffer, -1, -0.5, 0.5) 
            self.textureViewer.view(self.colorBuffer, -1, -1, 0.5) 
            
            text = __name__ + ": [LMB] camera, WSAD"
            
            self.textRenderer.add_str2d(3, 20, text) 
            self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK") 
            
            glfw.swap_buffers(self.window)  # swap the color buffers
            

            # Poll for window events. The key callback above will only be
            # invoked during this call.
            glfw.poll_events() 

    def run(self):
            print("Run")
            self.loop() 
            print("End")
            if bool(glDeleteProgram):
                glDeleteProgram(self.shaderProgram) 
            glfw.destroy_window(self.window)
            glfw.terminate()
            glfw.set_error_callback(None)