# ##
# Virtual camera, controls view transformation via observer position, azimuth
# and zenith (in radians). Eye position (the origin of camera coordinate set)
# can be at the observer position (1st person camera mode) or can orbit the
# observer position at the given radius (3rd person camera mode). Objects of
# the class are immutable.
# 
# @author PGRF FIM UHK
# rewrite PY: Matěj Kolář
# @version 2022-PY
# #
import math
from .Vec3D import Vec3D
from .Mat4ViewRH import Mat4ViewRH

class Camera:
    def __init__(self, pos = (0,0,0), azimuth = 0, zenith = 0, radius = 1, first_person = True):
        """Creates a camera with the given parameters

        Args:
            pos (tuple, optional): observer position. Defaults to (0, 0, 0).
            azimuth (int, optional): angle (in radians) between the xz and uv planes where v is the
                   view vector and u is the up vector, i.e. the vector considered
                   vertical by observer, i.e. the vector of the y-axis of the
                   camera coordinate set. Defaults to 0.
            zenith (int, optional): angle (in radians) between the view vector and z-axis. Defaults to 0.
            radius (int, optional): distance between the eye (camera origin) and the observer position in the 3rd person camera mode. Defaults to 1.
            firstPerson (bool, optional): boolean flag indicating 1st (true)/3rd (false) person camera mode. Defaults to True.
        """
        if isinstance(pos, Vec3D):
            self.pos = Vec3D().from_vec3(pos)
        else:
            self.pos = Vec3D().from_list(pos)
        self.azimuth = azimuth
        self.zenith = zenith
        self.radius = radius
        self.first_person = first_person
        self.view_vector = Vec3D((math.cos(azimuth) * math.cos(zenith)),
                (math.sin(azimuth) * math.cos(zenith)),
                math.sin(zenith))
        up_vector = Vec3D(
                (math.cos(azimuth) * math.cos(zenith + math.pi / 2)),
                (math.sin(azimuth) * math.cos(zenith + math.pi / 2)),
                math.sin(zenith + math.pi / 2))
        if first_person:
            eye = Vec3D().from_vec3(self.pos)
            self.view = Mat4ViewRH(self.pos, self.view_vector.mul_scal(radius), up_vector)
        else:
            eye = self.pos.add(self.view_vector.mul_scal(-radius))
            self.view = Mat4ViewRH(eye, self.view_vector.mul_scal(radius), up_vector)

    def add_azimuth(self,ang):
        """Returns a new camera with azimuth summed with the given value
            parameters: 
            ang: azimuth change in radians
        """
        return Camera(self.pos, self.azimuth + ang, self.zenith, self.radius, self.first_person)

    def add_radius(self, dist):
        """Returns a new camera with radius summed with the given value. Radius is kept >= 0.1
            parameters:
            dist: radius change amount
        """
        return Camera(self.pos, self.azimuth, self.zenith, max(self.radius + dist, 0.1), self.first_person)

    def add_zenith(self, ang):
        """Returns a new camera with zenith summed with the given value. Zenith is kept in [-pi/2, pi/2]
            parameters:
            ang: zenith change in radians
        """
        return Camera(self.pos, self.azimuth, max(-math.pi / 2, min(self.zenith + ang, math.pi / 2)), self.radius, self.first_person)

    def backward(self, speed):
        """Returns a new camera moved in the opposite direction of the view vector by the given distance
            parameters:
            speed: distance to move by
        """
        return self.forward(-speed)

    def down(self, speed):
        """Returns a new camera moved in the negative direction of z-axis by the given distance
            parameters:
            speed: distance to move by
        """
        return self.up(-speed)

    def forward(self, speed):
        """Returns a new camera moved in the direction of the view vector by the given distance
            parameters:
            speed: distance to move by            
        """
        return Camera(self.pos.add(self.view_vector.mul_scal(speed)), self.azimuth, self.zenith, self.radius, self.first_person)

    def left(self, speed):
        """Returns a new camera moved in the opposite direction of a cross product
            of the view vector and the up vector, i.e. to the left from the
            observer's perspective, by the given distance
            parameters:
            speed: distance to move by    
        """
        return self.right(-speed)

    def move(self, dir):
        """Returns a new camera moved by the given vector
            parameters:
            dir: vector to move by
        """
        return Camera(self.pos.add(dir), self.azimuth, self.zenith, self.radius, self.first_person)

    def mul_radius(self, scale):
        """Returns a new camera with radius multiplied by the given coefficient. Radius is kept >= 0.1
            parameters:
            scale: radius scale coefficient
        """
        return Camera(self.pos, self.azimuth, self.zenith, max(self.radius * scale, 0.1), self.first_person)

    def right(self, speed):
        """Returns a new camera moved in the direction of a cross product of the
            view vector and the up vector, i.e. to the right from the observer's
            perspective, by the given distance
            parameters:
            speed: distance to move by 
        """
        return Camera(self.pos.add(Vec3D(math.cos(self.azimuth-math.pi / 2),
                math.sin(self.azimuth - math.pi / 2), 0.0).mul_scal(speed)), self.azimuth, self.zenith, self.radius, self.first_person)
    
    def up(self, speed):
        """Returns a new camera moved in the direction of z-axis by the given distance
            parameters:
            speed: distance to move by 
        """
        return Camera(self.pos.add(Vec3D(0, 0, speed)), self.azimuth, self.zenith, self.radius, self.first_person)

    def with_azimuth(self, ang):
        """Returns a new camera with azimuth set to the given value
            parameters:
            ang: new azimuth value
        """
        return Camera(self.pos, ang, self.zenith, self.radius, self.first_person)

    def with_first_person(self, first_person):
        """Returns a new camera with 1st/3rd person camera mode flag set to the given value
            parameters:
            first_person: boolean flag indicating 1st (true) / 3rd (false) person camera
        """
        return Camera(self.pos, self.azimuth, self.zenith, self.radius, first_person) 

    def with_position(self, pos):
        """Returns a new camera with position set to the given vector
            parameters:
            pos: new position
        """
        return Camera(pos, self.azimuth, self.zenith, self.radius, self.first_person)

    def with_radius(self, radius):
        """Returns a new camera with radius (the distance between the eye (camera)
            and the observer in 3rd person camera mode) set to the given value
            parameters:
            radius: new radius value
        """
        return Camera(self.pos, self.azimuth, self.zenith, radius, self.first_person)

    def with_zenith(self, ang):
        """Returns a new camera with zenith set to the given value
            parameters:
            ang: new zenith value
        """
        return Camera(self.pos, self.azimuth, ang, self.radius, self.first_person)

    def to_string(self):
        return f"Camera()\n .withFirst_person({self.first_person})\n .withPosition({self.pos})\n .with_azimuth({self.azimuth})\n .with_zenith({self.zenith})\n.withRadius({self.radius})"