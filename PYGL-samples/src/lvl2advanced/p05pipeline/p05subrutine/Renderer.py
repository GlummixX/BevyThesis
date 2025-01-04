from transforms import Mat4Scale, Mat4PerspRH, Vec3D
from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer
import glfw
import math
from OpenGL.GL import *
from pyglutils import ShaderUtils, OGLBuffers, OGLUtils, OGLTextRenderer
import time as tm
from transforms.Camera import Camera
from __main__ import PATH


class Renderer(Abstract_renderer):
    """GLSL sample: Subroutine demonstration in both vAbstract_rendererertex and fragment shader
        author PGRF FIM UHK
        version 3.0-PY
        rewrite: Matěj Kolář
        since 10-2022
    """

    def __init__(self):
        self.mouse_button1 = False
        self.mode = 3
        self.function1 = 0
        self.function2 = 0
    
        self.cam = Camera()
        self.model = Mat4Scale(5, 5, 1)
    
        self.subroutine_color = [None]*3
        self.subroutine_shape = [None]*2


    def ws_callback(self, window, w, h):
        if w > 0 and h > 0:
            self.width = w
            self.height = h
            self.proj = Mat4PerspRH(math.pi / 4, self.height / self.width, 0.01, 1000.0)
            if self.textRenderer is not None:
                self.textRenderer.resize(self.width, self.height)
        
    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:# We will detect this in our rendering loop
            glfw.set_window_should_close(window, True) 
        if (action == glfw.PRESS or action == glfw.REPEAT):
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
            elif key == glfw.KEY_M:
                self.mode +=1
            elif key == glfw.KEY_KP_ADD or key == glfw.KEY_PAGE_DOWN:
                self.function1 +=1
            elif key == glfw.KEY_KP_SUBTRACT or key == glfw.KEY_PAGE_UP:
                self.function2 +=1
    
    def mb_callback(self, window, button, action, mods):
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            self.mouse_button1 = True
            self.ox, self.oy = glfw.get_cursor_pos(window)
            
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.RELEASE:
            self.mouse_button1 = False
            x,y = glfw.get_cursor_pos(window)
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width)
            self.ox = x
            self.oy = y

    
    def cp_callback(self, window, x, y):
        if self.mouse_button1:
            self.cam = self.cam.add_azimuth(math.pi * (self.ox - x) / self.width).add_zenith(math.pi * (self.oy - y) / self.width)
            self.ox = x
            self.oy = y
    
    def create_buffers(self, width, height):
        # triangles defined in vertex buffer
        cloud = [None]*width*height*3
        for i in range(0,width):
            for j in range(0,height):
                index = (i*height + j) * 3
                cloud[index] = j/(height-1) 
                cloud[index+1] = i/(width-1) 
                cloud[index+2] = 0 

        attributes = [OGLBuffers.Attrib("inPosition", 3)]

        #create geometry without index buffer as the point list 
        self.buffers = OGLBuffers.OGLBuffers(cloud, None, attributes)
        
        print(self.buffers)

    def init(self):
        OGLUtils.shader_check()

        OGLUtils.print_OGL_parameters()

        self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p05subrutine/colored")
        
        if "ARB_explicit_uniform_location" in OGLUtils.get_extensions():
                self.shader_program = ShaderUtils.load_program_directory(PATH+"shaders/lvl2advanced/p05pipeline/p05subrutine/coloredLayout")
        
        self.create_buffers(100, 100)

        self.locMat = glGetUniformLocation(self.shader_program, "matMVP")
        self.locTime = glGetUniformLocation(self.shader_program, "time")

        self.cam = self.cam.with_position(Vec3D(5, 5, 2.5)).with_azimuth(math.pi * 1.25).with_zenith(math.pi * -0.125)
        
        #FS subroutine definition
        self.subroutine_color = [None]*2

        if "ARB_explicit_uniform_location" in OGLUtils.get_extensions():
            self.subroutine_color = [None]*3
            # option 3 of fragment shader
            self.subroutine_color[2] = 4 # specific layout in VS
            self.locSub = glGetSubroutineUniformLocation(self.shader_program, GL_FRAGMENT_SHADER, "mySelection")

        # option 1 of fragment shader
        self.subroutine_color[0] = glGetSubroutineIndex(self.shader_program, GL_FRAGMENT_SHADER, "colorByColor")
        # option 2 of fragment shader
        self.subroutine_color[1] = glGetSubroutineIndex(self.shader_program, GL_FRAGMENT_SHADER, "colorByPossition")

        for i in range(0,len(self.subroutine_color)):
            print("Fragment subroutine_color ",i,": ", self.subroutine_color[i])
        
        # VS subroutine definition
        self.s = [None]*2

        self.s[0] = glGetSubroutineIndex(self.shader_program, GL_VERTEX_SHADER, "explicitFunction1")
        self.s[1] = glGetSubroutineIndex(self.shader_program, GL_VERTEX_SHADER, "explicitFunction2")

        for i in self.s:
            print("Vertex s ",i,": ", self.s[i])
        
        maxSub = glGetIntegerv(GL_MAX_SUBROUTINES)
        maxSubU = glGetIntegerv(GL_MAX_SUBROUTINE_UNIFORM_LOCATIONS)
        print("Max Subroutines: ", maxSub)
        print("Max Subroutine Uniforms: ", maxSubU)

        self.time = tm.perf_counter()

        self.textRenderer = OGLTextRenderer(self.width, self.height)
    
    def display(self):
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, self.width, self.height)
        currentTime = tm.perf_counter()
        
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glUseProgram(self.shader_program)
        
        glUniformSubroutinesuiv(GL_FRAGMENT_SHADER, 1, self.subroutine_color[self.function1 % len(self.subroutine_color)])
        glUniformSubroutinesuiv(GL_VERTEX_SHADER, 1, self.s[self.function2 % len(self.s)])
        
        glUniformMatrix4fv(self.locMat, 1, False,self.model.mul_mat4(self.cam.view).mul_mat4(self.proj).to_4x4array())
        
        glUniform1i(self.locTime, (int)(self.time - currentTime))
        text = "[LMB] camera, WSAD"

        glPointSize(1)

        mode = self.mode%4
        if mode == 0:
            text +=", [m]ode: points"
            self.buffers.draw(GL_POINTS, self.shader_program)
        elif mode == 1:
            text +=", [m]ode: lines"
            self.buffers.draw(GL_LINES, self.shader_program)
        elif mode == 2:
            text +=", [m]ode: line strip"
            self.buffers.draw(GL_LINE_STRIP, self.shader_program)
        elif mode == 3:
            glPointSize(10)
            text +=", [m]ode: bigger points"
            self.buffers.draw(GL_POINTS, self.shader_program)
        text +=", Num[+][-] change subrutine VS id: " + str(self.s[self.function2 % len(self.s)]) \
                + " FS id: " + str(self.subroutine_color[self.function1 % len(self.subroutine_color)])
            
        self.textRenderer.add_str2d(3, 20, text)
        self.textRenderer.add_str2d(self.width-90, self.height-3, " (c) PGRF UHK")
