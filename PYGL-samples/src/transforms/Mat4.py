import numpy as np
from .Vec3D import Vec3D

class Mat4:
    """A 4x4 matrix with common operations, immutable 
    @author PGRF FIM UHK 
    rewrite PY: Matěj Kolář
    @version 2022-PY
    """
    
    def __init__ (self, val = 0):
        """Creates a zero 4x4 matrix
            Providing value will result in 4x4 matrix with given value in every position
        """
        self.mat = np.zeros((4,4))
        if val != 0:
            self.mat.fill(val)

    def from_raw_rows(self, p1, p2, p3, p4):
        """Creates a 4x4 matrix from row vectors
            Rows should be list,tuple, or array

        Args:
            finalPoint3Dp1: row 0 vector (M00, M01, M02, M03)
            finalPoint3Dp2: row 1 vector (M10, M11, M12, M13)
            finalPoint3Dp3: row 2 vector (M20, M21, M22, M23)
            finalPoint3Dp4: row 3 vector (M30, M31, M32, M33)
        """
        self.mat[0] = p1
        self.mat[1] = p2
        self.mat[2] = p3
        self.mat[3] = p4
        return self

    def from_mat4(self,m:"Mat4"):
        """Creates a 4x4 matrix as a clone of the given 4x4 matrix
        Args:
            m (Mat4): 4x4 matrix to be cloned
        """
        self.mat = np.copy(m)
        return self
    
    def from_mat3(self, m:"Mat3"):
        """Creates a 4x4 matrix by filling a 3x3 submatrix of an identity 4x4 matrix

        Args:
            m (Mat3): 3x3 matrix to be copied to submatrix
        """
        self.mat[0] = [*m[0],0]
        self.mat[1] = [*m[1],0]
        self.mat[2] = [*m[2],0]
        self.mat[3][3] = 1
        return self

    def from_array(self, m):
        """Creates a 4x4 matrix row-wise from a 16-element array"""
        arr = np.asarray(m)
        self.mat = arr.reshape((4,4))
        return self

    def from_2darray(self, m):
        """Creates a 4x4 matrix from a 2 dimensional 4x4 array"""
        self.from_raw_rows(m[0],m[1],m[2],m[3])
        return self

    def add(self, m:"Mat4"):
        """Returns the result of element-wise summation with the given 4x4 matrix"""
        new_mat = Mat4()
        new_mat.mat = np.add(self.mat,m.mat)
        return new_mat

    def mul_scalar(self, d):
        """Returns the result of element-wise multiplication by the given scalar value"""
        new_mat = Mat4()
        new_mat.mat = np.multiply(self.mat,d)
        return new_mat

    def mul_mat4(self, m:"Mat4"):
        """Returns the result of matrix multiplication by the given 4x4 matrix"""
        new_mat = Mat4()
        new_mat.mat = np.matmul(self.mat,m.mat)
        return new_mat
    
    def copy(self):
        """Returns a copy of itself"""
        new_mat = Mat4()
        new_mat.mat = np.copy(self.mat)
        return new_mat

    def set_element(self, row:int, column:int, value):
        """Sets element on given coordinates to given value"""
        self.mat[row][column] = value

    def set_Row(self, index:int, row):
        """Sets row to given array of 4 values"""
        self.mat[index] = row

    def set_column(self, index:int, column):
        """Sets column to given array of 4 values"""
        self.mat[0][index] = column[0]
        self.mat[1][index] = column[1]
        self.mat[2][index] = column[2]
        self.mat[3][index] = column[3]

    def get(self, row:int, column:int):
        """Returns a matrix element"""
        return self.mat[row][column]

    def get_row(self, row:int):
        """Returns a row vector at the given index"""
        return tuple(self.mat[row])

    def get_column(self, column:int):
        """Returns a column vector at the given index"""
        return tuple(self.mat[0][column],self.mat[1][column],self.mat[2][column],self.mat[3][column])

    def get_translate(self):
        """Returns translation vector of matrix, (last row)"""
        return Vec3D(self.mat[3][0], self.mat[3][1], self.mat[3][2])

    def transpose(self):
        """Returns the transposition of this matrix"""
        result = Mat4()
        result.mat = np.transpose(self.mat)
        return result

    def det(self):
        """Returns the determinant of this matrix"""
        s0 = self.mat[0][0] * self.mat[1][1] - self.mat[1][0] * self.mat[0][1]
        s1 = self.mat[0][0] * self.mat[1][2] - self.mat[1][0] * self.mat[0][2]
        s2 = self.mat[0][0] * self.mat[1][3] - self.mat[1][0] * self.mat[0][3]
        s3 = self.mat[0][1] * self.mat[1][2] - self.mat[1][1] * self.mat[0][2]
        s4 = self.mat[0][1] * self.mat[1][3] - self.mat[1][1] * self.mat[0][3]
        s5 = self.mat[0][2] * self.mat[1][3] - self.mat[1][2] * self.mat[0][3]

        c5 = self.mat[2][2] * self.mat[3][3] - self.mat[3][2] * self.mat[2][3]
        c4 = self.mat[2][1] * self.mat[3][3] - self.mat[3][1] * self.mat[2][3]
        c3 = self.mat[2][1] * self.mat[3][2] - self.mat[3][1] * self.mat[2][2]
        c2 = self.mat[2][0] * self.mat[3][3] - self.mat[3][0] * self.mat[2][3]
        c1 = self.mat[2][0] * self.mat[3][2] - self.mat[3][0] * self.mat[2][2]
        c0 = self.mat[2][0] * self.mat[3][1] - self.mat[3][0] * self.mat[2][1]
        return s0 * c5 - s1 * c4 + s2 * c3 + s3 * c2 - s4 * c1 + s5 * c0

    def inverse(self):
        """Returns the inverse of this matrix if it exists or None"""
        s0 = self.mat[0][0] * self.mat[1][1] - self.mat[1][0] * self.mat[0][1]
        s1 = self.mat[0][0] * self.mat[1][2] - self.mat[1][0] * self.mat[0][2]
        s2 = self.mat[0][0] * self.mat[1][3] - self.mat[1][0] * self.mat[0][3]
        s3 = self.mat[0][1] * self.mat[1][2] - self.mat[1][1] * self.mat[0][2]
        s4 = self.mat[0][1] * self.mat[1][3] - self.mat[1][1] * self.mat[0][3]
        s5 = self.mat[0][2] * self.mat[1][3] - self.mat[1][2] * self.mat[0][3]

        c5 = self.mat[2][2] * self.mat[3][3] - self.mat[3][2] * self.mat[2][3]
        c4 = self.mat[2][1] * self.mat[3][3] - self.mat[3][1] * self.mat[2][3]
        c3 = self.mat[2][1] * self.mat[3][2] - self.mat[3][1] * self.mat[2][2]
        c2 = self.mat[2][0] * self.mat[3][3] - self.mat[3][0] * self.mat[2][3]
        c1 = self.mat[2][0] * self.mat[3][2] - self.mat[3][0] * self.mat[2][2]
        c0 = self.mat[2][0] * self.mat[3][1] - self.mat[3][0] * self.mat[2][1]
        det = s0 * c5 - s1 * c4 + s2 * c3 + s3 * c2 - s4 * c1 + s5 * c0

        if det == 0:
            return None

        iDet = 1 / det
        res = Mat4()
        res.mat[0][0] = ( self.mat[1][1] * c5 - self.mat[1][2] * c4 + self.mat[1][3] * c3) * iDet
        res.mat[0][1] = (-self.mat[0][1] * c5 + self.mat[0][2] * c4 - self.mat[0][3] * c3) * iDet
        res.mat[0][2] = ( self.mat[3][1] * s5 - self.mat[3][2] * s4 + self.mat[3][3] * s3) * iDet
        res.mat[0][3] = (-self.mat[2][1] * s5 + self.mat[2][2] * s4 - self.mat[2][3] * s3) * iDet

        res.mat[1][0] = (-self.mat[1][0] * c5 + self.mat[1][2] * c2 - self.mat[1][3] * c1) * iDet
        res.mat[1][1] = ( self.mat[0][0] * c5 - self.mat[0][2] * c2 + self.mat[0][3] * c1) * iDet
        res.mat[1][2] = (-self.mat[3][0] * s5 + self.mat[3][2] * s2 - self.mat[3][3] * s1) * iDet
        res.mat[1][3] = ( self.mat[2][0] * s5 - self.mat[2][2] * s2 + self.mat[2][3] * s1) * iDet

        res.mat[2][0] = ( self.mat[1][0] * c4 - self.mat[1][1] * c2 + self.mat[1][3] * c0) * iDet
        res.mat[2][1] = (-self.mat[0][0] * c4 + self.mat[0][1] * c2 - self.mat[0][3] * c0) * iDet
        res.mat[2][2] = ( self.mat[3][0] * s4 - self.mat[3][1] * s2 + self.mat[3][3] * s0) * iDet
        res.mat[2][3] = (-self.mat[2][0] * s4 + self.mat[2][1] * s2 - self.mat[2][3] * s0) * iDet

        res.mat[3][0] = (-self.mat[1][0] * c3 + self.mat[1][1] * c1 - self.mat[1][2] * c0) * iDet
        res.mat[3][1] = ( self.mat[0][0] * c3 - self.mat[0][1] * c1 + self.mat[0][2] * c0) * iDet
        res.mat[3][2] = (-self.mat[3][0] * s3 + self.mat[3][1] * s1 - self.mat[3][2] * s0) * iDet
        res.mat[3][3] = ( self.mat[2][0] * s3 - self.mat[2][1] * s1 + self.mat[2][2] * s0) * iDet
        return res

    def to_array(self):
        """Returns this matrix stored row-wise in a array"""
        return self.copy().mat.flatten()
    
    def to_4x4array(self):
        """Returns this matrix stored as 4x4 array"""
        return self.copy().mat

    def equals(self,obj):
        """Compares this object against the specified object."""
        return self == obj or obj is not None and isinstance(self,Mat4)\
            and (obj.get_row(0) == self.get_row(0)).all()\
            and (obj.get_row(1) == self.get_row(1)).all()\
            and (obj.get_row(2) == self.get_row(2)).all()\
            and (obj.get_row(3) == self.get_row(3)).all()
    
    def __str__(self):
        return str(self.mat)