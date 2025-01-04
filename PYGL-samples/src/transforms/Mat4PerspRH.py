import math
from .Mat4Identity import Mat4Identity

class Mat4PerspRH(Mat4Identity):
    """A 4x4 matrix of right-handed perspective visibility volume to normalized clipping volume transformation
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """

    def __init__(self, alpha, k, zn, zf):
        """Creates a 4x4 transformation matrix equivalent to the mapping of an
            perspective visibility volume (an axis-aligned frustum symmetrical about
            xz and yz planes) of given dimensions to the normalized clipping volume
            ([-1,1]x[-1,1]x[0,1])

        Args:
            alpha: vertical field of view angle in radians
            k: volume height/width ratio
            zn: distance to the near clipping plane along z-axis
            zf: distance to the far clipping plane along z-axis
        """
        super().__init__()
        h = (1.0 / math.tan(alpha / 2.0))
        w = k * h
        self.mat[0][0] = w
        self.mat[1][1] = h
        self.mat[2][2] = zf / (zn - zf)
        self.mat[3][2] = zn * zf / (zn - zf)
        self.mat[2][3] = -1.0
        self.mat[3][3] = 0.0
