import math
from Mathf import Mathf

class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def Dot(self, other) -> float:
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def Cross(self, other) -> 'Vector3':
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x

        return Vector3(x, y, z)

    # Returns the angle between 2 vectors using Lambert's cosine law
    def Angle(self, other) -> float:
        dotProd = self.Dot(other)
        magProd = self.Magnitude * other.Magnitude
        cosThetaRadians = dotProd / magProd

        return math.degrees(math.acos(cosThetaRadians))

    def Scale(self: 'Vector3', scalar: float):
        self *= scalar

    @staticmethod
    def Lerp(a: 'Vector3', b: 'Vector3', interpolant: float) -> 'Vector3':
        x = Mathf.Lerp(a.x, b.x, interpolant)
        y = Mathf.Lerp(a.y, b.y, interpolant)
        z = Mathf.Lerp(a.z, b.z, interpolant)

        return Vector3(x, y, z)

    def Lerp(self, other) -> 'Vector3':
        return Vector3.Lerp(self, other)

    @staticmethod
    def Distance(a: 'Vector3', b: 'Vector3') -> float:
        return (a - b).Magnitude

    @staticmethod
    def Midpoint(a: 'Vector3', b: 'Vector3') -> 'Vector3':
        return Vector3((a + b) / 2.0)

    @property
    def SqrMagnitude(self) -> float:
        return (self.x**2) + (self.y**2) + (self.z**2)

    @property
    def Magnitude(self) -> float:
        return math.sqrt(self.SqrMagnitude)

    def ToString(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return self.ToString()

    def PolarString(self, other) -> str:
        net = self + other
        inclination = net.Angle(Vector3(net.x, net.y, 0.0))

        return f"<{round(net.Magnitude, 2)}, {round(inclination, 2)}>"

    def Equals(self, other) -> float:
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def __add__(self, other) -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other) -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other) -> 'Vector3':
        return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)

    def __truediv__(self, other) -> 'Vector3':
        return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)

    def __eq___(self, other) -> bool:
        return self.Equals(other)

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __getitem__(self, idx: int) -> float:
        match idx:
            case 0: return self.x
            case 1: return self.y
            case 2: return self.z
            case _: return math.nan
