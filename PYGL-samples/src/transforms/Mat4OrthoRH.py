from .Mat4Identity import Mat4Identity

class Mat4OrthoRH(Mat4Identity):
    """A 4x4 matrix of right-handed orthogonal visibility volume to normalized clipping volume transformation
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """

    def __init__(self, w, h, zn, zf):
        """Creates a 4x4 transformation matrix equivalent to the mapping of an
            orthogonal visibility volume (an axis-aligned cuboid symmetrical about xz
            and yz planes) of given dimensions to the normalized clipping volume
            ([-1,1]x[-1,1]x[0,1])

        Args:
            w: visibility cuboid width
            h: visibility cuboid height
            zn: distance to the near clipping plane along z-axis
            zf: distance to the far clipping plane along z-axis
        """
        super().__init__()
        self.mat[0][0] = 2.0 / w
        self.mat[1][1] = 2.0 / h
        self.mat[2][2] = 1.0 / (zn - zf)
        self.mat[3][2] = zn / (zn - zf)
