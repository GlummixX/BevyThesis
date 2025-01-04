from .Mat4 import Mat4
from .Mat4RotX import Mat4RotX
from .Mat4RotY import Mat4RotY
from .Mat4RotZ import Mat4RotZ


class Mat4RotXYZ(Mat4):
    """A 4x4 matrix of sequential right-handed rotation about x, y and z axes
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """

    def __init__(self, alpha, beta, gamma):
        """Creates a 4x4 transformation matrix equivalent to right-handed rotations
            about x, y and z axes chained in sequence in this order

        Args:
            alpha : rotation angle about x-axis, in radians
            beta : rotation angle about y-axis, in radians
            gamma :  rotation angle about z-axis, in radians
        """
        super.__init__()
        self.from_mat4(Mat4RotX(alpha).mul_mat4(Mat4RotY(beta)).mul_mat4(Mat4RotZ(gamma)))
