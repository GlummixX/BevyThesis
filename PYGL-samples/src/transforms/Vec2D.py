import math

 
class Vec2D:
    """2D vector over real numbers (final double-precision), equivalent to 2D affine point, immutable
        @author PGRF FIM UHK
        PY rewrite: Kolář Matěj
        @version 2022-PY
    """
    
    def __init__(self,x = None, y = None):
        """Creates a 2D vector"""
        if x is None and y is None:
            self.x = 0
            self.y = 0
        elif x is not None and y is None:
            self.x = x
            self.y = x
        elif x is not None and y is not None:
            self.x = x
            self.y = y 
    
    def __iter__(self):
        return iter((self.x, self.y))

    def from_vec2d(self, v):
        """Creates a vector by cloning the give one"""
        self.x = v.x
        self.y = v.y
        return self
  
    def from_list(self, l):
        self.x = l[0]
        self.y = l[1]
        return self
  
    def to_array(self):
        return((self.x,self.y))

    def add(self, v):
        """Returns the result of vector addition of the given vector as a new vector"""
        return Vec2D(self.x + v.x, self.y + v.y)

    def sub(self, v):
        """Returns the result of vector subtraction of the given vector as a new vector"""
        return Vec2D(self.x - v.x, self.y - v.y)
    
    def mul_scalar(self, d):
        """Returns the result of scalar multiplication as a new vector"""
        return Vec2D(self.x * d, self.y * d)
    
    def mul_vec(self, v):
        """Returns the result of element-wise multiplication with the given vector as a new vector"""
        return Vec2D(self.x * v.x, self.y * v.y)
    
    def dot(self, v):
        """Returns the result of dot-product with the given vector"""
        return self.x * v.x + self.y * v.y

    def normalized(self):
        """Returns a collinear unit vector (by dividing all vector components by
             vector length) if possible (nonzero length), None otherwise"""
        len = self.length()
        if (len == 0.0):
            return None
        return Vec2D(self.x / len, self.y / len)

    def opposite(self):
        """Returns the vector opposite to this vector"""
        return Vec2D(-self.x, -self.y)
    
    def length(self):
        """Returns the length of this vector"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def equals(self, obj):
        """Compares this object against the specified object."""
        return self == obj or obj != None and isinstance(obj,Vec2D) and self.x == obj.x and self.y == obj.y