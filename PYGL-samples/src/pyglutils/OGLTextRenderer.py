from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from . import ShaderUtils, OGLBuffers
from transforms import Mat4Scale, Mat4Transl, Mat4RotZ
import math
            
class OGLTextRenderer:
    def __init__(self, width, height, font = None):
        """Create TextRenderer object

        Args:
            width (int):  width of output rendering frame
            height (int): height of output rendering frame
            font (String, optional): font. Defaults to arial.
        """
        self.textureID = -1
        w = width
        h = height
        if width < 8:
            w = 8
        if height < 8:
            h = 8
        self.resize(w, h)
        self.viewer = Viewer()
        self.color = (255,255,255,255)#floats
        self.bgColor = (0,0,0,255)#float
        self.rotationAngle = 0
        self.scale = 1
        
        if font is None:
            self.font = ImageFont.truetype("arial.ttf", 12, 0)
        else:
            self.font = font

    def resize(self, width, height):
        """Update size of output rendering frame
        Args:
            width (int): updated width of output rendering frame
            height (int): updated height of output rendering frame
        """
        if width <= 0:
            return
        if height <= 0:
            return
        self.width = width
        self.height = height
        if not glIsTexture(self.textureID): self.textureID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textureID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def add_str2d(self, x, y, s):
        """Draw string on 2D coordinates of the raster frame

        Args:
            x (int): x position of string in range < 0, width-1 > of raster frame
            y (int): y position of string in range < 0, height-1 > of raster frame
            s (String): string to draw
        """
        if s != "":
            h = math.ceil(self.font.size/8)*8
            w = int(len(s)*(self.font.size*0.67))
            self.img = Image.new("RGB", (w,h))
            draw = ImageDraw.Draw(self.img)
            draw.rectangle((0, 0, w, h), fill = (0,0,0,0))
            draw.rectangle((0, 0, w, h), fill = self.bgColor)
            draw.text((0, 0), s, fill=self.color, font=self.font)

            glBindTexture(GL_TEXTURE_2D, self.textureID)
            img = np.asarray(self.img.convert("RGBA"),dtype=np.ubyte) #convert("RGB")
            img = np.flipud(img)
            glBindTexture(GL_TEXTURE_2D, self.textureID)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

            #glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,self.width,self,self.height,0,GL_RGBA,GL_UNSIGNED_BYTE,img)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, img)
            glViewport(-self.width, -self.height, 2*self.width, 2*self.height)

            self.viewer.view(self.textureID, x/self.width, 1-y/self.height, w/self.width, h/self.height, self.rotationAngle, self.scale)
                
 
class Viewer:

    def __init__(self):
        self.buffers = self.create_buffers()
        
        self.SHADER_FRAG_SRC = [
                "#version 330\n", 
                "in vec2 texCoords;", 
                "out vec4 fragColor;", 
                "uniform sampler2D drawTexture;", 
                "void main() {", 
                "     fragColor = texture(drawTexture, texCoords);", 
                "}"
        ]
        self.SHADER_VERT_SRC = [
                "#version 330\n", 
                "in vec2 inPosition;", 
                "in vec2 inTexCoord;", 
                "uniform mat4 matTrans;", 
                "out vec2 texCoords;", 
                "void main() {", 
                "    gl_Position = matTrans*vec4(inPosition , 0.0f, 1.0f);", 
                "   texCoords = inTexCoord;", 
                "}"
        ]

        self.shaderProgram = ShaderUtils.load_program_src(self.SHADER_VERT_SRC, self.SHADER_FRAG_SRC)
        self.locMat = glGetUniformLocation(self.shaderProgram, "matTrans")

    def create_buffers(self):
        vertexBufferData = [
                0, 0, 0, 0, 
                1, 0, 1, 0, 
                0, 1, 0, 1, 
                1, 1, 1, 1 ]
        indexBufferData = [ 0, 1, 2, 3 ]

        attributes = [OGLBuffers.Attrib("inPosition", 2), OGLBuffers.Attrib("inTexCoord", 2) ]

        return OGLBuffers.OGLBuffers(vertexBufferData, None, attributes, indexBufferData)

    def view(self, textureID, x, y, w, h, rotationAngle, scale):
        if glIsProgram(self.shaderProgram):
            #glPushAttrib(GL_DEPTH_BUFFER_BIT|GL_ENABLE_BIT)
            sp = glGetIntegerv(GL_CURRENT_PROGRAM)
            glUseProgram(self.shaderProgram)
            glActiveTexture(GL_TEXTURE0)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            scale_mat = Mat4Scale(w,h,1)
            scale_scale_mat = Mat4Scale(scale)
            rot_mat = Mat4RotZ(rotationAngle)
            transl_mat = Mat4Transl(x,y,0)
            glUniformMatrix4fv(self.locMat, 1, False, scale_mat.mul_mat4(scale_scale_mat).mul_mat4(rot_mat).mul_mat4(transl_mat).to_4x4array())
            glBindTexture(GL_TEXTURE_2D, textureID)
            glUniform1i(glGetUniformLocation(self.shaderProgram, "drawTexture"), 0)
            self.buffers.draw(GL_TRIANGLE_STRIP, self.shaderProgram)
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glUseProgram(sp)
            #glPopAttrib()