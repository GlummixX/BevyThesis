from .AbstractRenderer import Abstract_renderer


class Renderer(Abstract_renderer):
    """author PGRF FIM UHK
        version 2.0-PY
        rewrite: Matěj Kolář
        since 10-2022
    """


    def key_callback(self, window, key, scancode, action, mods):
        pass

    def ws_callback(self, window, w, h):
        pass

    def mb_callback(self, window, button, action, mods):
        pass
    
    def cp_callbacknewinvoke(self, window, x, y):
        pass

    def scroll_callback(self, window, dx, dy):
        pass