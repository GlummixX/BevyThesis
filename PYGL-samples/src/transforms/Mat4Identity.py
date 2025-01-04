from .Mat4 import Mat4

class Mat4Identity(Mat4):
    """A 4x4 identity matrix
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY

    """
    def __init__(self):
        """Creates an identity 4x4 matrix"""
        super().__init__()
        for i in range(0,4):
            self.mat[i][i] = 1

