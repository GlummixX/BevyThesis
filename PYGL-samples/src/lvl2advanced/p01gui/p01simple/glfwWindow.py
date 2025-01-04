import glfw
import sys
from .AbstractRenderer import Abstract_renderer

WIDTH = 600
HEIGHT = 400

class glfwWindow:

    def __init__(self,renderer:"Abstract_renderer", width = WIDTH, height = HEIGHT, debug = False) -> None:
        self.renderer = renderer
        self.debug = debug
        self.width = width
        self.height = height
        self.window = None
        if debug :
            print("Run in debugging mode")
        self.run()

    
    def run(self):
        self.init()
        
        self.loop()

        self.renderer.dispose()
        
        #destroy the window
        glfw.destroy_window(self.window)

        # Terminate GLFW and free the error callback
        glfw.terminate()
        glfw.set_error_callback(None)
        
    def err(self,*args):
        print("ERROR - GLFW: ",args)
        
    def debug_err_callback(self, error, description):
        if (error == glfw.VERSION_UNAVAILABLE):
            print("ERROR - GLFW: GLFW_VERSION_UNAVAILABLE: This demo requires OpenGL 2.0 or higher.")
        if (error == glfw.NOT_INITIALIZED):
            print("")
        if (error == glfw.NO_CURRENT_CONTEXT):
            print("ERROR - GLFW: GLFW_NO_CURRENT_CONTEXT")
        if (error == glfw.INVALID_ENUM):
            print("ERROR - GLFW: GLFW_INVALID_ENUM")
        if (error == glfw.INVALID_VALUE):
            print("ERROR - GLFW: GLFW_INVALID_VALUE")
        if (error == glfw.OUT_OF_MEMORY):
            print("ERROR - GLFW: GLFW_OUT_OF_MEMORY")
        if (error == glfw.API_UNAVAILABLE):
            print("ERROR - GLFW: GLFW_API_UNAVAILABLE")
        if (error == glfw.VERSION_UNAVAILABLE):
            print("ERROR - GLFW: GLFW_VERSION_UNAVAILABLE")
        if (error == glfw.PLATFORM_ERROR):
            print("ERROR - GLFW: GLFW_PLATFORM_ERROR")
        if (error == glfw.FORMAT_UNAVAILABLE):
            print("ERROR - GLFW: GLFW_FORMAT_UNAVAILABLE")
        if (error == glfw.FORMAT_UNAVAILABLE):
            print("ERROR - GLFW: GLFW_FORMAT_UNAVAILABLE")
        

    def init(self):
        # Setup an error callback. The default implementation
        # will print the error message in System.err.
        glfw.set_error_callback(self.err)

        # Initialize GLFW. Most GLFW functions will not work before doing this.
        if not glfw.init():
            print("ERROR - GLFW: Unable to initialize GLFW")
            sys.exit(1)

        # Configure GLFW
        glfw.default_window_hints(); # optional, the current window hints are already the default
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE); # the window will stay hidden after creation
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE); # the window will be resizable

        text = __name__
        # Create the window
        self.window = glfw.create_window(self.width, self.height, text, None, None)
        if self.window == None:
            print("ERROR - GLFW: Failed to create the GLFW window")
            sys.exit(1)

        # Setup a key callback. It will be called every time a key is pressed, repeated or released.
        glfw.set_key_callback(self.window, self.renderer.key_callback)
        glfw.set_window_size_callback(self.window, self.renderer.ws_callback)
        glfw.set_mouse_button_callback(self.window, self.renderer.mb_callback)
        glfw.set_cursor_pos_callback(self.window, self.renderer.cp_callback)
        glfw.set_scroll_callback(self.window, self.renderer.scroll_callback)
        
        if self.debug:
            glfw.set_error_callback(self.debug_err_callback)
        
        # Get the thread stack and push a new frame
        try:
            # Get the window size passed to glfwCreateWindow
            pWidth, pHeight = glfw.get_window_size(self.window)

            #Get the resolution of the primary monitor
            vidmode = glfw.get_video_mode(glfw.get_primary_monitor())

            # Center the window
            glfw.set_window_pos(self.window,(vidmode.width() - pWidth.get(0)) / 2,(vidmode.height() - pHeight.get(0)) / 2)
            
        # the stack frame is popped automatically
        except:pass
    

        # Make the OpenGL context current
        glfw.make_context_current(self.window)
        # Enable v-sync
        glfw.swap_interval(1)

        # Make the window visible
        glfw.show_window(self.window)

    def loop(self):
        # This line is critical for LWJGL's interoperation with GLFW's
        # OpenGL context, or any context that is managed externally.
        # LWJGL detects the context that is current in the current thread,
        # creates the GLCapabilities instance and makes the OpenGL
        # bindings available for use.
        ### Not as important for python i would say
        # GL.createCapabilities();

        #if self.debug:
        #    GLUtil.setupDebugMessageCallback()

        self.renderer.ws_callback(self.window, self.width, self.height)

        self.renderer.init()


        # Run the rendering loop until the user has attempted to close
        # the window or has pressed the ESCAPE key.
        while not glfw.window_should_close(self.window):
            
            self.renderer.display()

            glfw.swap_buffers(self.window) # swap the color buffers


            # Poll for window events. The key callback above will only be
            # invoked during this call.
            glfw.poll_events()
