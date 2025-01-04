from OpenGL.GL import *
from .OGLTexture2D import OGLTexture2D
from . import OGLTexImageFloat

class OGLRenderTarget:
    def from_whcf(self, width, height, count = 1, format = None):
        if format is None:
            format = OGLTexImageFloat.Format(4)
        self.from_all(width, height, count, None, format)
        return self

    def from_tex_image(self, count, texImage):
        self.from_all(texImage.get_width(), texImage.get_height(), count, [texImage], texImage.get_format())
        return self

    def from_tex_images(self, texImage):
        self.from_all(texImage[0].get_width(), texImage[0].get_height(), len(texImage), texImage ,texImage[0].get_format())
        return self

    def from_all(self, width, height, count, tex_image, format):
        self.width = width
        self.height = height
        self.count = count
        self.color_buffers = [None]*count
        self.draw_buffers = [None]*count
        for i in range(0, count):
            if tex_image is None:
                image_data = None
            else:
                image_data = tex_image[i].get_data_buffer()
            self.color_buffers[i] = OGLTexture2D().from_raw(width, height, format.get_internal_format(), format.get_pixel_format(), format.get_pixel_type(), image_data)
            self.draw_buffers[i] = GL_COLOR_ATTACHMENT0 + i
        
        self.depth_buffer =  OGLTexture2D().from_raw(width, height, GL_DEPTH_COMPONENT, GL_DEPTH_COMPONENT,GL_FLOAT, None)
        
        self.frame_buffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        for i in range(0,count):
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D,self.color_buffers[i].textureID, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D,self.depth_buffer.textureID, 0)
        
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
            print("ERROR: There is a problem with the FBO")
            
        return self

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.frame_buffer)
        glDrawBuffers(self.draw_buffers)
        glViewport(0, 0, self.width, self.height)

    def bind_color_texture(self, shaderProgram, name, slot, bufferIndex = 0):
        self.color_buffers[bufferIndex].bind_slot(shaderProgram, name, slot)

    def bind_depth_texture(self, shaderProgram, name, slot):
        self.depth_buffer.bind_slot(shaderProgram, name, slot)

    def get_color_texture(self, bufferIndex = 0):
        if (bufferIndex < self.number_color_textures()):
            return self.color_buffers[bufferIndex]
        return self.color_buffers[0]

    def get_depth_texture(self):
        return self.depth_buffer

    def number_color_textures(self):
        return len(self.color_buffers)
