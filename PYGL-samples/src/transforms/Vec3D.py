import math
from . import Vec2D

class Vec3D:
    """
    3D vector over real numbers (final double-precision), equivalent to 3D affine
    point, immutable

    @author PGRF FIM UHK
    PY rewrite: Kolář Matěj
    @version 2022-PY
    """

    def __init__(self, x=None, y=None, z=None):
        """Creates a 3D vector"""

        if x is None and y is None and z is None:
            self.x = 0
            self.y = 0
            self.z = 0
        elif x is not None and y is None and z is None:
            self.x = x
            self.y = x
            self.z = x
        elif x is not None and y is not None and z is not None:
            self.x = x
            self.y = y
            self.z = z
            
    def __iter__(self):
        return iter((self.x, self.y, self.z))
        
    def from_vec3(self, vec3):
        self.x = vec3.x
        self.y = vec3.y
        self.z = vec3.z
        return self

    
    def from_list(self, array):
        if len(array) >=3:
            self.x = array[0]
            self.y = array[1]
            self.z = array[2]
        return self

    def to_array(self):
        return([self.x, self.y, self.z])
    
    def ignoreZ(self):
        return Vec2D(self.x, self.y)

    def add(self,v):
        return Vec3D(self.x + v.x, self.y + v.y, self.z + v.z)

    def sub(self, v):
        return Vec3D(self.x - v.x, self.y - v.y, self.z - v.z)

    def mul_scal(self, d):
        """Scalar multiplication"""
        return Vec3D(self.x * d, self.y * d, self.z * d)

    def mul_mat(self, m):
        """Returns the result of multiplication by the given 3x3 matrix"""
        return Vec3D(
            m.mat[0][0] * self.x + m.mat[1][0] * self.y + m.mat[2][0] * self.z,
            m.mat[0][1] * self.x + m.mat[1][1] * self.y + m.mat[2][1] * self.z,
            m.mat[0][2] * self.x + m.mat[1][2] * self.y + m.mat[2][2] * self.z)

    def mul_quat(self, q):
        """Returns the result of applying the given quaternion to this vector"""
        #final Quat p = q.mulR(new Quat(0, x, y, z)).mulR(q.inverse());
        #return new Vec3D(p.i, p.j, p.k);
        t = q.getIJK().mul(2).cross(self)
        return self.add(t.mul(q.getR())).add(q.getIJK().cross(t))

    def mul_vec(self, v):
        """Returns the result of element-wise multiplication with the given vector"""
        return Vec3D(self.x * v.x, self.y * v.y, self.z * v.z)

    def dot(self, v):
        """Returns the result of dot-product with the given vector"""
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        """Returns the result of cross-product with the given vector, i.e. a vector
            perpendicular to both this and the given vector, the direction is
             right-handed"""
        return Vec3D(self.y * v.z - self.z * v.y, self.z * v.x - self.x * v.z, self.x * v.y - self.y* v.x)

    def normalized(self):
        """Returns a collinear unit vector (by dividing all vector components by
             vector length) if possible (nonzero length), None otherwise"""
        len = self.length()
        if (len == 0.0):
            return None
        return Vec3D(self.x / len, self.y / len, self.z / len)

    def opposite(self):
        """Returns the vector opposite to this vector"""
        return Vec3D(-self.x, -self.y, -self.z)

    def length(self):
        """Returns the length of this vector"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def equals(self, obj):
        """Compares this object against the specified object."""
        return self == obj or obj != None and isinstance(obj,Vec3D) and self.x == obj.x and self.y == obj.y and self.z == obj.z