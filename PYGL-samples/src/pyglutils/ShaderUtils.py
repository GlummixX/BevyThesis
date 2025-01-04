from OpenGL.GL import *
from OpenGL.GLU import *
import os

VERTEX_SHADER_EXTENSION = ".vert"
FRAGMENT_SHADER_EXTENSION = ".frag"
GEOMETRY_SHADER_EXTENSION = ".geom"
TESS_CONTROL_SHADER_EXTENSION = ".tesc"
TESS_EVALUATION_SHADER_EXTENSION = ".tese"
COMPUTE_SHADER_EXTENSION = ".comp"

VERTEX_SHADER_SUPPORT_VERSION = 120
FRAGMENT_SHADER_SUPPORT_VERSION = 120
GEOMETRY_SHADER_SUPPORT_VERSION = 150
TESSELATION_SUPPORT_VERSION = 400
COMPUTE_SHADER_SUPPORT_VERSION = 430

SHADER_FILE_EXTENSIONS = [VERTEX_SHADER_EXTENSION, FRAGMENT_SHADER_EXTENSION, 
        GEOMETRY_SHADER_EXTENSION, TESS_CONTROL_SHADER_EXTENSION, TESS_EVALUATION_SHADER_EXTENSION, 
        COMPUTE_SHADER_EXTENSION]

SHADER_SUPPORT_EXTENSIONS = [ VERTEX_SHADER_SUPPORT_VERSION, 
        FRAGMENT_SHADER_SUPPORT_VERSION, GEOMETRY_SHADER_SUPPORT_VERSION, TESSELATION_SUPPORT_VERSION, 
        TESSELATION_SUPPORT_VERSION, COMPUTE_SHADER_SUPPORT_VERSION]

SHADER_NAME_CONSTANTS = [ GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, 
        GL_GEOMETRY_SHADER, GL_TESS_CONTROL_SHADER, GL_TESS_EVALUATION_SHADER, GL_COMPUTE_SHADER]

SHADER_NAMES = [ "Vertex", "Fragment", "Geometry", "Control", "Evaluation", "Compute" ]


# Load, create, compile, attach and link shader sources defined as files
# 
# @param gl
#            GL context
# @param vertexShaderFileName
#            full path name of vertex shader file with/without file
#            extension (VERTEX_SHADER_EXTENSION) or None
# @param fragmentShaderFileName
#            full path name of fragment shader file with/without file
#            extension (FRAGMENT_SHADER_EXTENSION) or None
# @param geometryShaderFileName
#            full path name of geometry shader file with/without file
#            extension (GEOMETRY_SHADER_EXTENSION) or None
# @param tessControlShaderFileName
#            full path name of control shader file with/without file
#            extension (TESS_CONTROL_SHADER_EXTENSION) or None
# @param tessEvaluationShaderFileName
#            full path name of evaluation shader file with/without file
#            extension (TESS_EVALUATION_SHADER_EXTENSION) or None
# @param computeShaderFileName
#            full path name of compute shader file with/without file
#            extension (COMPUTE_SHADER_EXTENSION) or None
# @param functionBeforeLinking
#               function called before linking shader program, 
#               int-valued argument defines shader program id 
# @return new id of shader program



def load_program_directory(path):
    name = path.split("/")[-1]
    stat = path.replace("/"+name, "")
    files = os.listdir(path.replace("/"+name, ""))
    shaders = []
    for file in files:
        if name == file.split(".")[0]:
            shaders.append(stat+"/"+file)
    return load_program_list(shaders)

def load_program_src(vertexShader = None, fragmentShader = None, geometryShader = None, tessControlShader = None, tessEvaluationShader = None, computeShader = None, functionBeforeLinking = None):
    data = [[vertexShader, 0], [fragmentShader, 1], [geometryShader, 2], [tessControlShader, 3], [tessEvaluationShader, 4], [computeShader, 5]]
    return load_program_src_array(data, functionBeforeLinking)

def load_program_specific(vertexShaderFileName = None, fragmentShaderFileName = None, geometryShaderFileName = None, tessControlShaderFileName = None, tessEvaluationShaderFileName = None, computeShaderFileName = None, functionBeforeLinking = None):
    shaderFileNames = list(range(len(SHADER_FILE_EXTENSIONS)))
    shaderFileNames[0] = vertexShaderFileName
    shaderFileNames[1] = fragmentShaderFileName
    shaderFileNames[2] = geometryShaderFileName
    shaderFileNames[3] = tessControlShaderFileName
    shaderFileNames[4] = tessEvaluationShaderFileName
    shaderFileNames[5] = computeShaderFileName
    return load_program_list(shaderFileNames, functionBeforeLinking)

# Read shader code as stream from file
# 
# @param streamFileName
#            full path name to a shader file
# @return array of Strings with GLSL shader code
def read_shader_program(streamFileName):
    with open(streamFileName, "r") as f:
        res = f.readlines()
    return res

def load_program_list(shaderFileNames, functionBeforeLinking = None):
    if len(shaderFileNames) > len(SHADER_NAMES):
        print("Number of shader sources is bigger than number of shaders")
        return -1
    
    shaderSrcArray = list(range(0, len(SHADER_FILE_EXTENSIONS)))
    for i in range(0, len(shaderFileNames)):
        if shaderFileNames[i] is None:
            shaderSrcArray[i] = None
            continue

        if "." not in  shaderFileNames[i]:
            shaderFileNames[i] += SHADER_FILE_EXTENSIONS[i]
            shader_type_id = i
        else:
            for ext in SHADER_FILE_EXTENSIONS:
                if ext in shaderFileNames[i]:
                    shader_type_id = SHADER_FILE_EXTENSIONS.index(ext)
                    break
            

        print("Shader file: ", shaderFileNames[i], " Reading ... ", end="")

        shaderSrc = read_shader_program(shaderFileNames[i])
        if shaderSrc is None:
            shaderSrcArray[i] = None
            continue
        else:
            print("OK")
            shaderSrcArray[i] = [shaderSrc, shader_type_id]
    for i in shaderSrcArray:
        if type(i) == type(1):
            shaderSrcArray[i] = None
    return load_program_src_array(shaderSrcArray, functionBeforeLinking)


# Load, create, compile, attach and link shader sources defined as arrays
# of Strings
# 
# @param gl
#            GL context
# @param shaderSrcArray
#            array of arrays of Strings with GLSL codes for shaders in
#            order vertex, fragment, geometry, control, evaluation and
#            compute shader or None
# @param functionBeforeLinking
#               function called before linking shader program, 
#               int-valued argument defines shader program id 
# @return new id of shader program

def load_program_src_array(shaderSrcArray, functionBeforeLinking = None):
    #OGLUtils.emptyGLError()
    if len(shaderSrcArray) > len(SHADER_NAMES):
        print("Number of shader sources is bigger than number of shaders")
        return -1

    shaderProgram = glCreateProgram()
    if shaderProgram < 0:
        print("Unable create new shader program ")
        return -1
    
    print("New shader program '", shaderProgram, "' created")

    shaders = list(range(0, len(shaderSrcArray)))
    for i in shaders:
        shaders[i] = 0
        if shaderSrcArray[i] == None:
            continue
        if shaderSrcArray[i][0] == None:
            continue
        print("  " + SHADER_FILE_EXTENSIONS[i] + " shader: Creating ... ", end = "")
        #TODO
        #if (OGLUtils.getVersionGLSL() < SHADER_SUPPORT_EXTENSIONS[i]) {
        #    print(SHADER_NAMES[i] + " shader extension is not supported by OpenGL driver ("
        #            + OGLUtils.getVersionGLSL() + ").")
        #    continue
        #}
        
        shaders[i] = create_shader_program(shaderSrcArray[i][0], SHADER_NAME_CONSTANTS[shaderSrcArray[i][1]])
        if shaders[i] > 0 :
            print(shaders[i], "OK")
        else:
            print("Shader is not supported")
            continue

        print("  Compiling ", shaders[i], "... ", end = "")
        shaders[i] = compile_shader_program(shaders[i])
        if (shaders[i] > 0):
            print("OK")
        else:
            return -1

        print("  Attaching ", shaders[i], " to ", shaderProgram, "... ", end = "")
        glAttachShader(shaderProgram, shaders[i])
        print("OK")

    if (shaders[0] <= 0 and shaders[-1] <= 0): #no vertex or compute shader
        print("No vertex or compute shader available \n")
        return -1
    
    if functionBeforeLinking is not None:
        functionBeforeLinking.accept(shaderProgram)
    
    print("Linking shader program ", shaderProgram , "... ", end = "")
    if link_program(shaderProgram):
        print("OK")
    else:
        # We don't need the program anymore
        glDeleteProgram(shaderProgram)

    for shader in shaders:
        if (shader > 0):
            # Always detach shaders after a successful link
            glDetachShader(shaderProgram, shader)
            # Don't leak shader either
            if glIsShader(shader):
                glDeleteShader(shader)

    return shaderProgram




#    
# Create shader and define source as array of Strings. At the end of a
# String of code line is char \n added. Chars after // are deleted.
# 
# @param gl
#           GL context
# @param shaderSrc
#           array of Strings with GLSL shader code
# @param type
#           of shader
# @return new id of shader
# 
def create_shader_program(shaderSrc, type):
    shader = glCreateShader(type)
    if (shader <= 0):
        return shader
    glShaderSource(shader, shaderSrc)
    return shader

# Compile shader
# 
# @param gl
#            GL context
# @param shader
#            id of shader
# @return new id of shader
def compile_shader_program(shader):
    glCompileShader(shader)
    error = check_log_info(shader, GL_COMPILE_STATUS)
    if (error == None):
        return shader
    else:
        print("failed")
        print(error)
        if shader > 0:
            glDeleteShader(shader)
        return -1

# Link shader program
# 
# @param gl
#            GL context
# @param shader
#            id of shader program
# @return new id of shader program

def link_program(shaderProgram):
    glLinkProgram(shaderProgram)
    error = check_log_info(shaderProgram, GL_LINK_STATUS)
    if (error == None):
        return True
    else:
        print("failed\n", error.decode())
        return False


def check_log_info(programObject, mode):
    if mode == GL_COMPILE_STATUS:
        return check_log_info_shader(programObject, mode)
    elif mode == GL_VALIDATE_STATUS or mode ==  GL_LINK_STATUS:
        return check_log_info_program(programObject, mode)
    else:
        return "Unsupported mode."

def check_log_info_shader(programObject, mode):
    err = glGetShaderiv(programObject, mode)
    if (err != GL_TRUE):
        len = glGetShaderiv(programObject, GL_INFO_LOG_LENGTH)
        if (len == 0):
            return None
        return glGetShaderInfoLog(programObject)
    return None

def check_log_info_program(programObject, mode):
    err = glGetProgramiv(programObject, mode)
    if (err != GL_TRUE):
        len = glGetProgramiv(programObject, GL_INFO_LOG_LENGTH)
        if len == 0:
            return None
        return glGetProgramInfoLog(programObject)
    return None
