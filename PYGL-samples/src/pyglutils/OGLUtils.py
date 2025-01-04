from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from .ShaderUtils import GEOMETRY_SHADER_SUPPORT_VERSION, TESSELATION_SUPPORT_VERSION, COMPUTE_SHADER_SUPPORT_VERSION

def print_OGL_parameters():
    """Print version, vendor and extensions of current OpenGL
    """
    
    print("GL vendor:", glGetString(GL_VENDOR).decode())
    print("GL renderer:", glGetString(GL_RENDERER).decode())
    print("GL version:", glGetString(GL_VERSION).decode())
    print("GL shading language version:", glGetString(GL_SHADING_LANGUAGE_VERSION).decode(), " (#version", get_version_GLSL(), ")")
    print("GL extensions:", get_extensions())
    print("GLSL version:", get_version_GLSL())
    print("OpenGL extensions:", get_version_OpenGL())

def get_extensions():
    """Get extensions of actual OpenGL """
    if get_version_GLSL() < get_version_OpenGL():
        #Deprecated in newer versions
        ext = glGetString(GL_EXTENSIONS).decode()
    else:
        number_extensions = glGetIntegerv(GL_NUM_EXTENSIONS)
        ext = glGetStringi(GL_EXTENSIONS,1).decode()
        for i in range(1,number_extensions):
            ext = ext + " " + glGetStringi(GL_EXTENSIONS,i).decode()
    return ext

def get_version_GLSL():
    """Get supported GLSL version

    Returns:
        int: version as integer number multiplied by 100, for GLSL 1.4 return 140, for GLSL 4.5 return 450, ...
    """
    version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode()
    parts = version.replace("'","").replace("'","").replace(" - ",".").replace(" ",".")
    parts = parts.split(".")
    version_number = int(parts[0]) * 100 + int(parts[1])
    return version_number

def get_version_OpenGL():
    """Get supported OpenGL version

    Returns:
        int: return version as integer number multiplied by 100, for OpenGL 3.3 return 330, ...
    """
    version = glGetString(GL_VERSION).decode()
    parts = version.replace("b'","").replace("'","").replace(" ",".")
    parts = parts.split(".")
    return int(parts[0]) * 100 + int(parts[1]) * 10 


def shader_check():
    """Check OpenGL shaders support"""
    ext = glGetString(GL_EXTENSIONS).decode()
    if ((get_version_GLSL() < get_version_OpenGL()) and not "GL_ARB_vertex_shader" in ext or not "GL_ARB_fragment_shader" in ext):
        print("Shaders are not available.")
        sys.exit(1)

    print("This OpenGL (#version", get_version_GLSL(), ") supports:\n vertex and fragment shader")

    if get_version_GLSL() >= GEOMETRY_SHADER_SUPPORT_VERSION or "geometry_shader"in ext:
        print(" geometry shader")
    if get_version_GLSL() >= TESSELATION_SUPPORT_VERSION or "tessellation_shader" in ext:
        print(" tessellation")
    if get_version_GLSL() >= COMPUTE_SHADER_SUPPORT_VERSION or "compute_shader" in ext:
        print(" compute shader")


def check_GL_error__(text,longReport = False):
    """Check GL error

    Args:
        longReport: type of report
    """
    err = glGetError()
    while (err != GL_NO_ERROR):

        if err == GL_INVALID_ENUM:
            errorName = "GL_INVALID_ENUM"
            errorDesc = "An unacceptable value is specified for an enumerated argument. The offending command is ignored and has no other side effect than to set the error flag."
            break
        elif err == GL_INVALID_VALUE:
            errorName = "GL_INVALID_VALUE"
            errorDesc = "A numeric argument is out of range. The offending command is ignored and has no other side effect than to set the error flag."
            break
        elif err == GL_INVALID_OPERATION:
            errorName = "GL_INVALID_OPERATION"
            errorDesc = "The specified operation is not allowed in the current state. The offending command is ignored and has no other side effect than to set the error flag."
            break
        elif err == GL_INVALID_FRAMEBUFFER_OPERATION:
            errorName = "GL_INVALID_FRAMEBUFFER_OPERATION"
            errorDesc = "The framebuffer object is not complete. The offending command is ignored and has no other side effect than to set the error flag."
            break
        elif err == GL_OUT_OF_MEMORY:
            errorName = "GL_OUT_OF_MEMORY"
            errorDesc = "There is not enough memory left to execute the command. The state of the GL is undefined, except for the state of the error flags, after this error is recorded."
            break
        if longReport:
            print(text + " GL error: " + err + " " + errorName + ": " + errorDesc)
        else:
            print(text + " GL error: " + errorName)
        err = glGetError()

def empty_GL_error():
    """Empty GL error"""
    err = glGetError()
    while (err != GL_NO_ERROR):
        err = glGetError()

def check_GL_error(text = ""):
    """Check GL error"""
    check_GL_error__(text, False)


def get_debug_source(code):
    if code == 0x8246:
        return "GL_DEBUG_SOURCE_API"
    elif code == 0x8247:
        return "GL_DEBUG_SOURCE_WINDOW_SYSTEM"
    elif code == 0x8248:
        return "GL_DEBUG_SOURCE_SHADER_COMPILER"
    elif code == 0x8249:
        return "GL_DEBUG_SOURCE_THIRD_PARTY"
    elif code == 0x824A:
        return "GL_DEBUG_SOURCE_APPLICATION"
    elif code == 0x824B:
        return "GL_DEBUG_SOURCE_OTHER"
    return "GL_DEBUG_SOURCE_UNKNOWN"


def get_debug_type(code):
    if code == 0x824C:
        return "GL_DEBUG_TYPE_ERROR"
    elif code == 0x824D:
        return "GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR"
    elif code == 0x824E:
        return "GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR"
    elif code == 0x824F:
        return "GL_DEBUG_TYPE_PORTABILITY"
    elif code == 0x8250:
        return "GL_DEBUG_TYPE_PERFORMANCE"
    elif code == 0x8251:
        return "GL_DEBUG_TYPE_OTHER"
    elif code == 0x8268:
        return "GL_DEBUG_TYPE_MARKER"
    elif code == 0x8269:
        return "GL_DEBUG_TYPE_PUSH_GROUP"
    elif code == 0x826A:
        return "GL_DEBUG_TYPE_POP_GROUP"
    return "GL_DEBUG_TYPE_UNKNOWN"

def getDebugSeverity(code):
    if code == 0x9146:
        return "GL_DEBUG_SEVERITY_HIGH"
    elif code == 0x9147:
        return "GL_DEBUG_SEVERITY_MEDIUM"
    elif code == 0x9148:
        return "GL_DEBUG_SEVERITY_LOW"
    elif code == 0x826B:
        return "GL_DEBUG_SEVERITY_NOTIFICATION"

    return "GL_DEBUG_SEVERITY_UNKNOWN"
