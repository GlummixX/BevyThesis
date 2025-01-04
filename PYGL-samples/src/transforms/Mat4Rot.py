from .Mat4Identity import Mat4Identity
from .Vec3D import Vec3D
import math

class Mat4Rot(Mat4Identity):
    """A 4x4 matrix of right-handed rotation about general axis
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """
    
    def __init__(self):
        super().__init__()
    
    def angle(self, alpha, x, y, z):
        """Creates a 4x4 transformation matrix equivalent to right-handed rotation
            about general axis

        Args:
            alpha: rotation angle in radians
            x: x coordinate of rotation axis
            y: y coordinate of rotation axis
            z: z coordinate of rotation axis
        """
        return self.rotate(math.sin(alpha), math.cos(alpha), Vec3D(x, y, z))

    def rotate(self, sinAlpha, cosAlpha, rotAxis:"Vec3D"):
        """Creates a 4x4 transformation matrix equivalent to right-handed rotation about general axis

        Args:
            sinAlpha: sin of rotation angle
            cosAlpha: cos of rotation angle
            rotAxis (Vec3D): rotation axis
        """
        norm = rotAxis.normalized()
        if norm is None:
            return self
        ac = 1.0 - cosAlpha
        axis = norm

        self.mat[0][0] = axis.x * axis.x * ac + cosAlpha
        self.mat[0][1] = axis.x * axis.y * ac + axis.z * sinAlpha
        self.mat[0][2] = axis.x * axis.z * ac - axis.y * sinAlpha

        self.mat[1][0] = axis.y * axis.x * ac - axis.z * sinAlpha
        self.mat[1][1] = axis.y * axis.y * ac + cosAlpha
        self.mat[1][2] = axis.y * axis.z * ac + axis.x * sinAlpha

        self.mat[2][0] = axis.z * axis.x * ac + axis.y * sinAlpha
        self.mat[2][1] = axis.z * axis.y * ac - axis.x * sinAlpha
        self.mat[2][2] = axis.z * axis.z * ac + cosAlpha
        return self
 
    def vec3D_angle(self, alpha, axis:"Vec3D"):
        """Creates a 4x4 transformation matrix equivalent to right-handed rotation
            about general axis

        Args:
            alpha (_type_): rotation angle in radians
            axis (Vec3D): rotation axis
        """
        return self.rotate(math.sin(alpha), math.cos(alpha), axis)
