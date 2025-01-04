# path setting, may need to be changed depending on IDE, OS or root directory
PATH = "./" 

# imports of examples
from lvl1basic.p00.p01withoutShaders import l1p00p01
from lvl1basic.p00.p01withShader import l1p00p01shader
from lvl1basic.p00.p02withUtils import l1p00p02

from lvl1basic.p01start.p01buffer import l1p01p01
from lvl1basic.p01start.p02attribute import l1p01p02
from lvl1basic.p01start.p03uniform import l1p01p03
from lvl1basic.p01start.p04utils import l1p01p04
from lvl1basic.p01start.p05multiple import l1p01p05
from lvl1basic.p01start.p06depthbuffer import l1p01p06
from lvl1basic.p01start.p07text import l1p01p07

from lvl1basic.p02geometry.p01cube import l1p02p01
from lvl1basic.p02geometry.p02strip import l1p02p02
from lvl1basic.p02geometry.p03obj import l1p02p03

from lvl1basic.p03texture.p01intro import l1p03p01
from lvl1basic.p03texture.p02utils import l1p03p02
from lvl1basic.p03texture.p03multiple import l1p03p03

from lvl1basic.p04target.p01intro import l1p04p01
from lvl1basic.p04target.p02utils import l1p04p02
from lvl1basic.p04target.p03postproces import l1p04p03

from lvl2advanced.p01gui.p01simple.glfwWindow import glfwWindow
from lvl2advanced.p01gui.p01simple.AbstractRenderer import Abstract_renderer as l2p01p01

from lvl2advanced.p05pipeline.p01geometryshader.Renderer import Renderer as l2p05p01
from lvl2advanced.p05pipeline.p02tesselation.Renderer import Renderer as l2p05p02
from lvl2advanced.p05pipeline.p03query.Renderer import Renderer as l2p05p03
from lvl2advanced.p05pipeline.p05subrutine.Renderer import Renderer as l2p05p05

from lvl2advanced.p06compute.p01intro.Renderer import Renderer as l2p06p01
from lvl2advanced.p06compute.p02buffer.Renderer import Renderer as l2p06p02
from lvl2advanced.p06compute.p03texture.Renderer import Renderer as l2p06p03
from lvl2advanced.p06compute.p04game.Renderer import Renderer as l2p06p04
from lvl2advanced.p06compute.p05atomic.Renderer import Renderer as l2p06p05

# imports for menu
import glfw
import sys
from OpenGL.GL import *
from pyglutils import OGLTextRenderer
import math
import os

# Path warning #
def test_path():
    abs_path = os.path.abspath("").replace("\\","/")
    directory = os.listdir(PATH)
    if not "res" in directory:
        print("WARNING! - PATH setting seems invalid - res is not where expected, see line 2 of __main__.py")
        print(f"Path to root folder is: {abs_path}")
    directory = os.listdir(PATH+"res")
    if not "obj" in directory:
        print("WARNING! - PATH setting seems invalid - res/obj is not where expected, see line 2 of __main__.py")
        print(f"Path to root folder is: {abs_path}")
    directory = os.listdir(PATH+"shaders")
    if not "lvl1basic" in directory:
        print("WARNING! - PATH setting seems invalid - shaders/lvl1basic is not where expected, see line 2 of __main__.py")
        print(f"Path to root folder is: {abs_path}")

# Menu itself, not needed to tun the example, just for convinience#
class Main:
    def init(self):
        self.width = 300
        self.height = 300
        self.path="."

        print()
        print("########################################\n#------MENU CONSOLE OUTPUT FOLLOWS-----#\n########################################")
        print()

        if not glfw.init():
            print("Unable to initialize GLFW")
            sys.exit(1)

        glfw.default_window_hints() # optional, the current window hints are already the default
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE) # the window will stay hidden after creation
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE) # the window will be resizable
        self.window = glfw.create_window(self.width, self.height, "PGRF examples in PY", None, None)
        if self.window is None:
            print("Failed to create the GLFW window")
            sys.exit(1)

        # Setup a callback
        glfw.set_mouse_button_callback(self.window, self.mb_callback)
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_char_callback(self.window, self.character_callback)

        glfw.make_context_current(self.window) # Make the OpenGL context current
        glfw.swap_interval(0) # Enable v-sync
        glfw.show_window(self.window) # Make the window visible
        glClearColor(0.0, 0.0, 0.0, 1.0) # Set the clear color
        self.text_renderer = OGLTextRenderer(self.width, self.height)
        self.menu = {
            "1-Basic":{
                    "00":["01-Without shaders", "01-With shaders", "02-With utils"],
                    "01-Start":["01-Buffer", "02-Attribute", "03-Uniform", "04-Utils", "05-Multiple", "06-Depth buffer", "07-Text"],
                    "02-Geometry":["01-Cube", "02-Strip", "03-Obj"],
                    "03-Texture":["01-Intro","02-Utils","03-Multiple"],
                    "04-Target":["01-Intro", "02-Utils", "03-Postprocess"]
                },
            "2-Advanced":{
                "01-GUI":["01-Simple"],
                "05-Pipeline":["01-Geometry shader", "02-Tesselation", "03-Query", "05-Subrutine"],
                "06-Compute":["01-Intro","02-Buffer","03-Texture","04-Game","05-Atomic"]
                }
        }
        self.button_inst = self.buttons(self.path)
    
    def mb_callback(self, window, button, action, mods):
        x, y = glfw.get_cursor_pos(window)
        if button==glfw.MOUSE_BUTTON_1 and action == glfw.PRESS:
            for b in self.button_inst:
                res = b.colision(x,y)
                if res is not None:  
                    if res == ">EXIT<":
                        glfw.set_window_should_close(window, True) 
                    elif res == ">RETURN<":
                        self.path = ":".join(self.path.split(":")[0:-1])
                    else:
                        self.path += ":"+res
                    return

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.RELEASE:
            glfw.set_window_should_close(window, True)

    def character_callback(self, window, codepoint):
        option = chr(codepoint)
        if option.isnumeric:
            if int(option) < len(self.button_inst):
                res = self.button_inst[int(option)].act
                if res is not None:  
                    if res == ">EXIT<":
                        glfw.set_window_should_close(window, True) 
                    elif res == ">RETURN<":
                        self.path = ":".join(self.path.split(":")[0:-1])
                    else:
                        self.path += ":"+res
                    return

    def buttons(self, path:str):
        x = self.width/4
        buttons = []
        if path == ".":
            target = (*self.menu.keys(), ">EXIT<")
            off = int((self.height - len(target)*20)/2)
            for y, name in enumerate(target):
                buttons.append(Button(x, off+(y*20), name, name))
            return buttons
        else:
            path = path.split(":")
            if len(path) == 2:
                target = (*self.menu[path[-1]].keys(), ">RETURN<")
                off = int((self.height - len(target)*20)/2)
                for y, name in enumerate(target):
                    buttons.append(Button(x, off+(y*20), name, name))
                return buttons
            else:
                target = (*self.menu[path[1]][path[2]], ">RETURN<")
                off = int((self.height - len(target)*20)/2)
                for y, name in enumerate(target):
                    buttons.append(Button(x, off+(y*20), name, name))
                return buttons

    def loop(self, repath = ""):
        old = ""
        while not glfw.window_should_close(self.window):
            glViewport(0, 0, self.width, self.height)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the framebuffer
            self.text_renderer.add_str2d(self.width/4, 30, self.path[1:].replace(":", " "))
            self.text_renderer.add_str2d(3, self.height-25, "Click on options or use numbers from 0")
            self.text_renderer.add_str2d(3, self.height-5, "(c)Matěj Kolář & PGRF UHK")
            if self.path != old: 
                if repath != "": # load state after example end
                    self.path = repath
                    repath = ""
                if len(self.path.split(":")) <= 3:
                    self.button_inst = self.buttons(self.path) # create instances of buttons
                    old = self.path
                else:
                    return old, self.path # start example
            for b in self.button_inst:
                b.render(self.text_renderer) # render each button
            glfw.swap_buffers(self.window) # swap the color buffers
            glfw.poll_events()
    
    def run(self):
        self.init()
        old = ""
        while True:
            data = self.loop(old) # run menu loop, get results
            if data is not None: # in case of exit
                old, path = data
            else:
                break
            #make space in console output
            print()
            print("##########################################\n#-----EXAMPLE CONSOLE OUTPUT FOLLOWS-----#\n##########################################")
            print()
            # Start example #
            path_s = path[2:].split(":")
            if path_s[0] == "1-Basic":
                #raw start example:
                #l1p00p02.Main().run()
                if path_s[1] == "00":
                    if path_s[2] == "01-Without shaders": l1p00p01.Main().run()
                    elif path_s[2] == "01-With shaders": l1p00p01shader.Main().run()
                    elif path_s[2] == "02-With utils": l1p00p02.Main().run()
                elif path_s[1] == "01-Start": 
                    if path_s[2] == "01-Buffer": l1p01p01.Main().run()
                    elif path_s[2] == "02-Attribute": l1p01p02.Main().run()
                    elif path_s[2] == "03-Uniform": l1p01p03.Main().run()
                    elif path_s[2] == "04-Utils": l1p01p04.Main().run()
                    elif path_s[2] == "05-Multiple": l1p01p05.Main().run()
                    elif path_s[2] == "06-Depth buffer": l1p01p06.Main().run()
                    elif path_s[2] == "07-Text": l1p01p07.Main().run()
                elif path_s[1] == "02-Geometry": 
                    if path_s[2] == "01-Cube": l1p02p01.Main().run()
                    elif path_s[2] == "02-Strip": l1p02p02.Main().run()
                    elif path_s[2] == "03-Obj": l1p02p03.Main().run()
                elif path_s[1] == "03-Texture": 
                    if path_s[2] == "01-Intro": l1p03p01.Main().run()
                    elif path_s[2] == "02-Utils": l1p03p02.Main().run()
                    elif path_s[2] == "03-Multiple": l1p03p03.Main().run()
                elif path_s[1] == "04-Target": 
                    if path_s[2] == "01-Intro": l1p04p01.Main().run()
                    elif path_s[2] == "02-Utils": l1p04p02.Main().run()
                    elif path_s[2] == "03-Postprocess": l1p04p03.Main().run()
            else:
                #raw start example:
                #glfwWindow(l2p01p01())
                if path_s[1] == "01-GUI":
                    if path_s[2] == "01-Simple": renderer = l2p01p01()
                elif path_s[1] == "05-Pipeline":
                    if path_s[2] == "01-Geometry shader": renderer = l2p05p01()
                    elif path_s[2] == "02-Tesselation": renderer = l2p05p02()
                    elif path_s[2] == "03-Query": renderer = l2p05p03()
                    elif path_s[2] == "05-Subrutine": renderer = l2p05p05()
                elif path_s[1] == "06-Compute":
                    if path_s[2] == "01-Intro": renderer = l2p06p01()
                    elif path_s[2] == "02-Buffer": renderer = l2p06p02()
                    elif path_s[2] == "03-Texture": renderer = l2p06p03()
                    elif path_s[2] == "04-Game": renderer = l2p06p04()
                    elif path_s[2] == "05-Atomic": renderer = l2p06p05()
                else:
                    renderer = l2p01p01()
                glfwWindow(renderer)
            self.init() ## midloop re-init to handle glfw termination in examples

# Button class for ease of use #
class Button():
    def __init__(self, x, y, text, act):
        self.x = x
        self.y = y 
        self.text = text #what is rendered, change will have no effect on action when colision
        self.act = act #takes care of path, returned when colision, used for control
        # aprox. hitbox given font size is default -> 12px
        self.h = math.ceil(12/8)*8 
        self.w = int(len(text)*(12*0.67))

    def render(self, renderer:"OGLTextRenderer"):
        renderer.add_str2d(self.x, self.y, self.text)

    def colision(self, x, y):
        if (x > self.x and x < self.x+self.w) and (y < self.y and y > self.y-self.h):
            return self.act
        else:
            return None

# START #
if __name__ == "__main__":
    test_path() 
    Main().run()