from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
import glfw
from pyglutils import OGLTexture2D, ShaderUtils, OGLUtils, OGLTextRenderer, OGLTexImageFloat
import sys
from OpenGL.GL import *
from __main__ import PATH

class Renderer(Abstract_renderer):
    """ author: PGRF FIM UHK
        version: 2.0-PY
        rewrite: Matěj Kolář
        since: 10-2022
    """

    def __init__(self):
        self.mouse_down = 0
        self.mouseX = self.mouseY = 0
        self.inited = True
        self.clear = False
        self.compute = True
        self.continues = True
    
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True) # We will detect this in the rendering loop
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_M:
                self.compute = True
            elif key == glfw.KEY_N:
                self.continues = not self.continues
            elif key == glfw.KEY_I:
                self.inited = True
            elif key == glfw.KEY_C:
                self.clear = True
    
    def ws_callback(self, window, w, h):
        if (w > 0 and h > 0 and (w != self.width or h != self.height)):
            self.width = w
            self.height = h
            if (self.textRenderer is not None):
                self.textRenderer.resize(self.width, self.height)
    

    def mb_callback(self, window, button, action, mods):
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            self.mouse_down = 1
        
        if button==glfw.MOUSE_BUTTON_3 and action == glfw.PRESS:
            self.mouse_down = 2
        
        if self.mouse_down > 0:
            x,y = glfw.get_cursor_pos(window)
            self.mouseX = int(x)
            self.mouseY = int(y)
        
        if action == glfw.RELEASE:
            self.mouse_down = 0
    
    def cp_callback(self, window, x, y):
            if self.mouse_down > 0:
                self.mouseX = int(x)
                self.mouseY = int(y)

    def init_texture(self, clear):
        # load test texture
        try:
            self.texture = OGLTexture2D().from_file(PATH+"res/textures/mosaic.jpg")
        except Exception as e:
            print(e)
        
        if not clear:
            # create image as a copy of loaded texture, must have 4 components
            texImageIn = self.texture.get_tex_image(OGLTexImageFloat.Format(4))
        else:
            #/ create empty image with size same as loaded texture
            texImageIn = OGLTexImageFloat.OGLTexImageFloat().from_format(self.texture.width,
                self.texture.height, 1, OGLTexImageFloat.Format(4))
            # create input texture from the image
            x = texImageIn.get_width()/2
            y = texImageIn.get_height()/2
            #glider shape
            texImageIn.set_pixel_component(x-1, y, 0, 1.0) #only red color
            texImageIn.set_pixel_component(x+1, y, 0, 1.0) #only red color
            texImageIn.set_pixel_component(x+1, y+1, 0, 1.0) #only red color
            texImageIn.set_pixel_component(x, y+1, 0, 1.0) #only red color
            texImageIn.set_pixel_component(x+1, y-1, 0, 1.0) #only red color

        
        self.texture_in = OGLTexture2D().from_tex(texImageIn)
        # create empty image with size same as loaded texture
        texImageOut = OGLTexImageFloat.OGLTexImageFloat().from_format(self.texture.width,
                self.texture.height, 1, OGLTexImageFloat.Format(4))
        # create (empty) output texture from the image
        self.texture_out = OGLTexture2D().from_tex(texImageOut)

    
    def init(self):
        if OGLUtils.get_version_GLSL() < ShaderUtils.COMPUTE_SHADER_SUPPORT_VERSION \
                and "compute_shader" not in OGLUtils.get_extensions():
            print("Compute shader is not supported") 
            sys.exit(1)
        
        OGLUtils.print_OGL_parameters()
        
        #get limits of work group size per dimension
        for dim in range(0,3):
            val = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, dim)
            print("GL_MAX_COMPUTE_WORK_GROUP_SIZE [", dim, "] : ", val)
                
        self.compute_shader_program = ShaderUtils.load_program_specific(None, None, None, None, None, 
                PATH+"shaders/lvl2advanced/p06compute/p04game/computeLife") 
        
        self.texture_viewer = OGLTexture2D.Viewer()
        
        self.textRenderer = OGLTextRenderer(self.width, self.height)

    def display(self):
        glViewport(0, 0, self.width, self.height)
        
        if (self.inited):
            self.inited = False
            self.init_texture(False)
        
        if (self.clear):
            self.clear = False
            self.init_texture(True)
        
        
        w = self.texture.width
        h = self.texture.height
        
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # recompute? 
        if self.compute or self.continues:
            self.compute = False
            
            glBindImageTexture(0, self.texture_in.textureID, 0, False, 0, 
                    GL_READ_ONLY, GL_RGBA32F)
            glBindImageTexture(1, self.texture_out.textureID, 0, False, 0, 
                    GL_WRITE_ONLY, GL_RGBA32F)

            # first step
            glUseProgram(self.compute_shader_program)
            glDispatchCompute(int(w/16), int(h/16), 1)

            glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)


            #change textures 
            glBindImageTexture(0, self.texture_out.textureID, 0, False, 0, GL_READ_ONLY,
                    GL_RGBA32F)
            glBindImageTexture(1, self.texture_in.textureID, 0, False, 0, GL_WRITE_ONLY,
                    GL_RGBA32F)
            
            #second step
            glUseProgram(self.compute_shader_program)
            glDispatchCompute(int(w/16), int(h/16), 1)
            glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        
        if self.mouse_down > 0: #add new generator
            #print("[" + mouseX + "," + mouseY + "]")
            # get image as a copy of input texture
            texImageIn = self.texture_in.get_tex_image(OGLTexImageFloat.Format(4))
            x = 2 * self.mouseX * texImageIn.width / self.width
            y = 2 * self.mouseY * texImageIn.height / self.height
            if x > 0 and x <texImageIn.width-1 and y > 0 and y <texImageIn.height-1:
                if (self.mouse_down == 2):#cross shape		
                    texImageIn.set_pixel_component(x, y, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x+1, y, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x, y+1, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x-1, y, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x, y-1, 0, 1.0) #only red color
                
                if (self.mouse_down == 1):#glider shape
                    texImageIn.set_pixel_component(x-1, y, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x+1, y, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x+1, y+1, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x, y+1, 0, 1.0) #only red color
                    texImageIn.set_pixel_component(x+1, y-1, 0, 1.0) #only red color
            
            # update input texture from the image
            self.texture_in.set_tex_image(texImageIn)
        
        
        #draw textures

        #show original texture in right up corner
        self.texture_viewer.view(self.texture.textureID,0,0)
        #show input texture in left up corner
        self.texture_viewer.view(self.texture_in.textureID,-1,0)
        #show output texture in right down corner
        self.texture_viewer.view(self.texture_out.textureID, 0, -1)
        
        
        text = __name__ + ": [LMB] new life, [n] -start/stop, [m] - step, [i] - reset, [c]lear, ESC - exit "
        
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")