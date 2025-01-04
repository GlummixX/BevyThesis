from transforms import Mat4PerspRH, Mat4Scale
from transforms.Camera import Camera
from pyglutils import ShaderUtils, OGLUtils, OGLRenderTarget, OGLTexture2D, OGLTextRenderer, OGLBuffers
from OpenGL.GL import *
import math
import glfw
import sys
from __main__ import PATH

class Main:
    """GLSL sample:<br/>
        Draw two different geometries with two different shader programs<br/>
        Requires LWJGL3

        @author PGRF FIM UHK
        @version 3.0-PY
        rewrite: Matěj Kolář
        @since 10-2022
    """
    
    def __init__(self):
        self.width = 300
        self.height = 300
        self.mouse_button1 = False
        self.ox = 0
        self.oy = 0
    
        self.cam = Camera()
        self.proj = Mat4PerspRH(math.pi / 4, 1, 1, 10.0)
        
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

        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl1basic/p04target/p02utils/texture")

        glUseProgram(self.shader_program)
        
        self.locMat = glGetUniformLocation(self.shader_program, "mat")
        
        self.render_target = OGLRenderTarget().from_whcf(512, 512,1)

        self.cam = self.cam.with_position((5, 5, 2.5)).with_azimuth(math.pi * 1.25).with_zenith(math.pi * -0.125)
        
        try:
            self.texture = OGLTexture2D().from_file(PATH+"res/textures/mosaic.jpg")
        except Exception as e:
            print(e)

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        self.texture_viewer = OGLTexture2D.Viewer()
        
        self.text_renderer = OGLTextRenderer(self.width, self.height)	
        
    def key_callback(self,window, key, scancode, action, mods):
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
            proj = Mat4PerspRH(math.pi / 4, self.height / self.width, 1, 10.0)
            if self.text_renderer is not None:
                self.text_renderer.resize(self.width, self.height)


    
    
    def create_buffers(self):
        # vertices are not shared among triangles (and thus faces) so each face
        # can have a correct normal in all vertices
        # also because of this, the vertices can be directly drawn as GL_TRIANGLES
        # (three and three vertices form one face) 
        # triangles defined in index buffer
        cube = [
                # bottom (z-) face
                1, 0, 0,	0, 0, -1, 	1, 0,
                0, 0, 0,	0, 0, -1,	0, 0, 
                1, 1, 0,	0, 0, -1,	1, 1, 
                0, 1, 0,	0, 0, -1,	0, 1, 
                # top (z+) face
                1, 0, 1,	0, 0, 1,	1, 0, 
                0, 0, 1,	0, 0, 1,	0, 0, 
                1, 1, 1,	0, 0, 1,	1, 1,
                0, 1, 1,	0, 0, 1,	0, 1,
                # x+ face
                1, 1, 0,	1, 0, 0,	1, 0,
                1, 0, 0,	1, 0, 0,	0, 0, 
                1, 1, 1,	1, 0, 0,	1, 1,
                1, 0, 1,	1, 0, 0,	0, 1,
                # x- face
                0, 1, 0,	-1, 0, 0,	1, 0,
                0, 0, 0,	-1, 0, 0,	0, 0, 
                0, 1, 1,	-1, 0, 0,	1, 1,
                0, 0, 1,	-1, 0, 0,	0, 1,
                # y+ face
                1, 1, 0,	0, 1, 0,	1, 0,
                0, 1, 0,	0, 1, 0,	0, 0, 
                1, 1, 1,	0, 1, 0,	1, 1,
                0, 1, 1,	0, 1, 0,	0, 1,
                # y- face
                1, 0, 0,	0, -1, 0,	1, 0,
                0, 0, 0,	0, -1, 0,	0, 0, 
                1, 0, 1,	0, -1, 0,	1, 1,
                0, 0, 1,	0, -1, 0,	0, 1
            ]

        index_buffer_data = [None]*36
        for i in range(0,6):
            index_buffer_data[i*6] = i*4
            index_buffer_data[i*6 + 1] = i*4 + 1
            index_buffer_data[i*6 + 2] = i*4 + 2
            index_buffer_data[i*6 + 3] = i*4 + 1
            index_buffer_data[i*6 + 4] = i*4 + 2
            index_buffer_data[i*6 + 5] = i*4 + 3

                
                
        attributes = [OGLBuffers.Attrib("inPosition", 3),
                OGLBuffers.Attrib("inNormal", 3),
                OGLBuffers.Attrib("inTextureCoordinates", 2)]

        self.buffers = OGLBuffers.OGLBuffers(cube, None, attributes, index_buffer_data)

        print(self.buffers.to_string()) 

    def loop(self):
        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            glEnable(GL_DEPTH_TEST)
            glViewport(0, 0, self.width, self.height)
            
            # set our render target (texture)
            self.render_target.bind()

            glClearColor(0.7, 1.0, 1.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
            
            self.texture.bind_slot(self.shader_program, "textureID", 0)
            
            glUniformMatrix4fv(self.locMat, 1, False, self.cam.view.mul_mat4(self.proj).mul_mat4(Mat4Scale(self.width / self.height, 1, 1)).to_4x4array())
            
            # bind and draw
            self.buffers.draw(GL_TRIANGLES, self.shader_program)
            
            # set the default render target (screen)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.width, self.height)

            glClearColor(0.1, 0.1, 0.1, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
            
            # use the result of the previous draw as a texture for the next
            #self.render_target.bind_color_texture(self.shader_program, "textureID", 0)
            self.render_target.get_color_texture().bind_slot(self.shader_program, "textureID", 0)
            # use the depth buffer from the previous draw as a texture for the next
            #self.render_target.bind_depth_texture(self.shader_program, "textureID", 0)

            glUniformMatrix4fv(self.locMat, 1, False, self.cam.view.mul_mat4(self.proj).to_4x4array())
            self.buffers.draw(GL_TRIANGLES, self.shader_program)
            
            text = __name__ + ": [LMB] camera, WSAD"

            #OGLTexture2D depthTexture = renderTarget.getDepthTexture()
            #depthTexture.bind()
            #glTexParameteri(GL_TEXTURE_2D,
            #		GL_TEXTURE_COMPARE_MODE, GL_COMPARE_REF_TO_TEXTURE)

            self.texture_viewer.view(self.texture.textureID, -1, -1, 0.5)
            self.texture_viewer.view(self.render_target.get_color_texture().textureID, -1, -0.5, 0.5)
            self.render_target.get_depth_texture().bind()
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
            self.texture_viewer.view(self.render_target.get_depth_texture().textureID, -1, 0, 0.5)
            
          
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
        