from .Mat4Identity import Mat4Identity
from .Vec3D import Vec3D

class Mat4ViewRH(Mat4Identity):
    """A 4x4 matrix of right-handed view transformation
        @author PGRF FIM UHK
        rewrite PY: Matěj Kolář
        @version 2022-PY
    """
    
    def __init__(self, e:"Vec3D", v:"Vec3D", u:"Vec3D"):
        """Creates a 4x4 transition matrix from the current frame (coordinate
            system) to the observer (camera) frame described with respect to the
            current frame by origin position, view vector and up vector. The inherent
            observer frame is constructed orthonormal, specifically in {o, {x, y, z}}
            notation it is 
            {e, {normalize(u cross -v), normalize(-v cross (u cross -v)), normalize(-v)}} 
            where cross is the cross-product and normalize returns a collinear unit vector 
            (by dividing all vector components by vector length)

            @param e
                       eye, position of the observer frame origin with respect to the
                       current frame
            @param v
                       view vector, the direction of the observer frame -z axis with
                       respect to the current frame
            @param u
                       up vector, together with eye and view vector defines with
                       respect to the current frame the plane perpendicular to the
                       observer frame x axis (i.e. the plane in which lies the
                       observer frame y axis)
        """
        super().__init__()
        
        z = v.mul_scal(-1.0).normalized()
        if z == None: 
            z = Vec3D(1, 0, 0)
        x = u.cross(z).normalized()
        if x == None:
            x = Vec3D(1, 0, 0)
        y = z.cross(x)
        self.mat[0][0] = x.x
        self.mat[1][0] = x.y
        self.mat[2][0] = x.z
        self.mat[3][0] = -e.dot(x)
        self.mat[0][1] = y.x
        self.mat[1][1] = y.y
        self.mat[2][1] = y.z
        self.mat[3][1] = -e.dot(y)
        self.mat[0][2] = z.x
        self.mat[1][2] = z.y
        self.mat[2][2] = z.z
        self.mat[3][2] = -e.dot(z)
