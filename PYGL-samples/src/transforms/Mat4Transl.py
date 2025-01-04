from .Mat4Identity import Mat4Identity

class Mat4Transl(Mat4Identity):
    """A 4x4 matrix of translation
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """
    
    def __init__(self, x = 0, y = None, z = None):
        """Creates a 4x4 transformation matrix equivalent to translation in 3D

        Args:
            x (_type_): translation along x-axis
            y (_type_): translation along y-axis
            z (_type_): translation along z-axis
        """
        super().__init__()
        if y is None and z is None:
            y = x
            z = x
        self.mat[3][0] = x
        self.mat[3][1] = y
        self.mat[3][2] = z

    def from_vec3D(self, v):
        """Creates a 4x4 transformation matrix equivalent to translation in 3D from vec3D

        Args:
            v (Vec3D): Vec3 to create from
        """
        self.mat[3][0] = v.x
        self.mat[3][1] = v.y
        self.mat[3][2] = v.z
        return self
