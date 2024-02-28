import math
from Mathf import Mathf

class Vector2:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def Dot(self, other) -> float:
        return (self.x * other.x) + (self.y * other.y)

    def Scale(self, scalar: float):
        self *= scalar

    @staticmethod
    def Lerp(a: 'Vector2', b: 'Vector2', interpolant: float) -> 'Vector2':
        x = Mathf.Lerp(a.x, b.x, interpolant)
        y = Mathf.Lerp(a.y, b.y, interpolant)

        return Vector2(x, y)

    # Returns the angle between 2 vectors using Lambert's cosine law
    def Angle(self, other) -> float:
        dotProd = self.Dot(other)
        magProd = self.Magnitude * other.Magnitude
        cosThetaRadians = dotProd / magProd

        return math.degrees(math.acos(cosThetaRadians))

    def SetMagnitudeAndDirection(self, mag: float, dir: float):
        self.x = mag * math.cos(math.radians(dir))
        self.y = mag * math.sin(math.radians(dir))

    @property
    def SqrMagnitude(self) -> float:
        return (self.x**2) + (self.y**2)

    @property
    def Magnitude(self) -> float:
        return math.sqrt(self.SqrMagnitude)

    # Expresses the resultant of 2 vectors in the form <r, θ>
    @staticmethod
    def PolarString(a: 'Vector2', b: 'Vector2') -> str:
        net = a + b
        angle = net.Angle(Vector2(1.0, 0.0))    # net.x

        # TODO: There has to be a better way to do this.
        if (net.x > 0) and (net.y > 0): # First quadrant
            pass
        elif (net.x < 0) and (net.y > 0): # Second Quadrant
            angle += 90.0
        elif (net.x < 0) and (net.y < 0): # Third Quadrant
            angle += 180.0
        elif (net.x > 0) and (net.y < 0): # Fourth Quadrant
            angle += 270.0

        if angle > 360.0:
            angle = angle % 360.0

        return f"<{round(net.Magnitude, 2)}, {round(angle, 2)}>"

    def Equals(self, other) -> bool:
        return (self.x == other.x) and (self.y == other.y)

    def ToPolarString(self) -> str:
        return Vector2.PolarString(self, Vector2(0.0, 0.0))

    def ToString(self) -> str:
        return f"({self.x}, {self.y})"

    def __str__(self) -> str:
        return self.ToString()

    def __add__(self, other) -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> 'Vector2':
        return Vector2(self.x * other.x, self.y * other.y)

    def __truediv__(self, other) -> 'Vector2':
        return Vector2(self.x / other.x, self.y / other.y)

    def __eq__(self, other) -> bool:
        return self.Equals(other)

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __getitem__(self, idx: int) -> float:
        match idx:
            case 0: return self.x
            case 1: return self.y
            case _: return math.nan
