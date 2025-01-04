from OpenGL.GL import *
from OpenGL.GLU import *
from . import ShaderUtils, OGLBuffers, OGLTexImageFloat
from PIL import Image
import numpy as np
from transforms import Vec2D, Mat4Scale, Mat4Transl

class OGLTexture2D:
    
    class Viewer: #implements OGLTexture.Viewer
        def __init__(self, shaderProgram = None):
            self.buffers = self.create_buffers()
            self.shaderProgram = shaderProgram 
            
            self.SHADER_VERT_SRC = [
                    "#version 330\n", 
                    "in vec2 inPosition;\n", 
                    "in vec2 inTexCoord;\n", 
                    "uniform mat4 matTrans;\n", 
                    "out vec2 texCoords;\n", 
                    "void main() {\n", 
                    "    gl_Position = matTrans * vec4(inPosition , 0.0f, 1.0f);\n", 
                    "   texCoords = inTexCoord;\n", 
                    "}"]
            
            self.SHADER_FRAG_SRC = [ 
                    "#version 330\n", 
                    "in vec2 texCoords;\n", 
                    "out vec4 fragColor;\n", 
                    "uniform sampler2D drawTexture;\n", 
                    "uniform int level;\n", 
                    "void main() {\n", 
                    "     if (level >= 0)\n", 
                    "         fragColor = textureLod(drawTexture, texCoords, level);\n", 
                    "     else\n", 
                    "         fragColor = texture(drawTexture, texCoords);\n", 
                    "}"]
            if shaderProgram == None:
                self.shaderProgram = ShaderUtils.load_program_src(self.SHADER_VERT_SRC, self.SHADER_FRAG_SRC)
                
            self.locMat = glGetUniformLocation(self.shaderProgram, "matTrans")
            self.locLevel = glGetUniformLocation(self.shaderProgram, "level")
        
        def create_buffers(self):
            vertexBufferData = [
                    0, 0, 0, 0, 
                    1, 0, 1, 0, 
                    0, 1, 0, 1, 
                    1, 1, 1, 1 ]
            indexBufferData = [ 0, 1, 2, 3 ]

            attributes = [OGLBuffers.Attrib("inPosition", 2), OGLBuffers.Attrib("inTexCoord", 2) ]

            return OGLBuffers.OGLBuffers(vertexBufferData, None, attributes, indexBufferData)
        
        def view(self, textureID, x = -1, y = -1, scale = 1, aspectXY = 1, level = -1):
            self.view_vec2d(textureID, Vec2D(x, y), Vec2D(scale*aspectXY, scale), level)
        

        def view_vec2d(self, textureID, xy, scale, level):
            if glIsProgram(self.shaderProgram):
                #glPushAttrib(GL_DEPTH_BUFFER_BIT|GL_ENABLE_BIT)
                sp = glGetIntegerv(GL_CURRENT_PROGRAM)
                glUseProgram(self.shaderProgram)
                glActiveTexture(GL_TEXTURE0)
                glEnable(GL_TEXTURE_2D)
                scale_mat = Mat4Scale(scale.x, scale.y, 1)
                transl_mat = Mat4Transl(xy.x, xy.y, 0)
                glUniformMatrix4fv(self.locMat, 1, False, scale_mat.mul_mat4(transl_mat).to_4x4array())
                glUniform1i(self.locLevel, int(level))
                glBindTexture(GL_TEXTURE_2D, textureID)
                glUniform1i(glGetUniformLocation(self.shaderProgram, "drawTexture"), 0)
                self.buffers.draw(GL_TRIANGLE_STRIP, self.shaderProgram)
                glDisable(GL_TEXTURE_2D)
                glUseProgram(sp)
                #glPopAttrib()

        #def finalize() throws Throwable {
        #    super.finalize()
        #    //if (glIsProgram(shaderProgram))
        #    //    glDeleteProgram(shaderProgram)
        #}

    #
    # Reads the specified resource and returns the raw data as a ByteBuffer.
    #
    # @param resource   the resource to read
    # @param bufferSize the initial buffer size
    #
    # @return the resource data
    #
    # @throws IOException if an IO error occurs
    #
    def io_resource_to_byte_buffer(resource, bufferSize):
        image = Image.open(resource)
        return np.asarray(image.convert("RGBA"),dtype=np.ubyte)

    def __init__(self):
        pass
    
    def from_tex(self,image):
        self.from_raw(image.get_width(),image.get_height(), 
                image.get_format().get_internal_format(), image.get_format().get_pixel_format(), 
                image.get_format().get_pixel_type(),  image.get_data_buffer())
        return self

    def from_raw(self, width, height, internalFormat, pixelFormat, pixelType, buffer):
        self.width = width
        self.height = height
        
        self.textureID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textureID)
        if (pixelType == GL_FLOAT):
            glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, width, height, 0, pixelFormat, pixelType, buffer)
        if (pixelType == GL_UNSIGNED_BYTE):
            glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, width, height, 0, pixelFormat, pixelType, buffer)   
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        return self
    
    def from_file(self, fileName):
        print("Reading texture file ", fileName, end="... ")
        
        self.image = Image.open(fileName)
        w = self.image.width
        h = self.image.height
        data = np.asarray(self.image.convert("RGBA"),dtype=np.ubyte)
        
        print("OK [" + str(w) + "x" + str(h) + "]")

        self.width = w
        self.height = h
        self.textureID = glGenTextures(1)
        
        glBindTexture(GL_TEXTURE_2D, self.textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return self

    def flip_y(self):
        self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
        data = np.asarray(self.image.convert("RGBA"),dtype=np.ubyte)
        glBindTexture(GL_TEXTURE_2D, self.textureID)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.textureID)

    def bind_slot(self, shaderProgram, name, slot):
        glActiveTexture(GL_TEXTURE0 + slot)
        self.bind()
        loc = int(glGetUniformLocation(shaderProgram, name))
        glUniform1i(loc, slot)

    def bind_name(self, shaderProgram, name):
        self.bind(shaderProgram, name, 0)

    def to_buffered_image(self):
        self.bind()
        arr = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV)
        return arr

    def from_buffered_image(self, img):
        self.bind()
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL_RGBA, 
                GL_UNSIGNED_INT_8_8_8_8_REV, img)

    def get_texture_buffer(self,format, level = 0):
        self.bind()
        if isinstance(format,OGLTexImageFloat.Format):
            buffer = format.new_buffer(self.width >> level, self.height >> level)
            glGetTexImage(GL_TEXTURE_2D, level, format.get_pixel_format(), format.get_pixel_type(), buffer)
            return buffer
        
        #if (format instanceof OGLTexImageByte.Format) {
        #    ByteBuffer buffer = format.newBuffer(getWidth() >> level, getHeight() >> level);
        #    glGetTexImage(GL_TEXTURE_2D, level,  format.getPixelFormat(), format.getPixelType(), buffer);
        #    buffer.rewind();
        #    return buffer;
        
        return None
    

    def set_texture_buffer(self, format, buffer, level = 0):
        self.bind()
        if isinstance(format,OGLTexImageFloat.Format):
            glTexSubImage2D(GL_TEXTURE_2D, level, 0, 0, self.width >> level, self.height >> level, 
                format.get_pixel_format(), format.get_pixel_type(), buffer)
        #if (format instanceof OGLTexImageByte.Format) {
        #    glTexSubImage2D(GL_TEXTURE_2D, level, 0, 0, 
        #        getWidth() >> level, getHeight() >> level, 
        #        format.getPixelFormat(), format.getPixelType(), (ByteBuffer) buffer);}
        

    def set_tex_image(self, image, level = 0):
        self.set_texture_buffer(image.get_format(), image.get_data_buffer(), level)

    def get_tex_image(self, format, level = None):
        if level is not None:
            image = format.new_tex_image(self.width >> level, self.height >> level)
            image.set_data_buffer(self.get_texture_buffer(format, level))
            return image
        else:
            image = format.new_tex_image(self.width, self.height)
            image.set_data_buffer(self.get_texture_buffer(format))
            return image            
