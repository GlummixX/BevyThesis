from .Mat4Identity import Mat4Identity
import math

class Mat4RotX(Mat4Identity):
    """A 4x4 matrix of right-handed rotation about x-axis
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """
    def __init__(self, alpha):
        """Creates a 4x4 transformation matrix equivalent to right-handed rotation about x-axis

        Args:
            alpha : rotation angle in !radians!
        """
        super().__init__()
        self.mat[1][1] = math.cos(alpha)
        self.mat[2][2] = math.cos(alpha)
        self.mat[2][1] = -math.sin(alpha)
        self.mat[1][2] = math.sin(alpha)