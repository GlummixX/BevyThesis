from .Mat4Identity import Mat4Identity

class Mat4Scale(Mat4Identity):
    """A 4x4 matrix of 3D scaling
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """

    def __init__(self, x = 1, y = None, z = None):
        """Creates a 4x4 transformation matrix equivalent to scaling in 3D

        Args:
            x : x-axis scale factor
            y : y-axis scale factor
            z : z-axis scale factor
        """
        
        super().__init__()
        if y is None and z is None:
            y = x
            z = x

        self.mat[0][0] = x
        self.mat[1][1] = y
        self.mat[2][2] = z

    def from_vector(self, v):
        """Creates a 4x4 transformation matrix equivalent to scaling in 3D

        Args:
            v (Vec3D): vector scale factor
        """
        
        self.mat[0][0] = v.x
        self.mat[1][1] = v.y
        self.mat[2][2] = v.z
        return self