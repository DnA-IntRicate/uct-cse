from Mathf import Mathf
from Vector2 import Vector2
from Vector3 import Vector3

v1 = Vector2(10, 0)
v2 = Vector2(2, 10)
print(v1.Angle(v2))

a = Vector2(3, 5)
b = Vector2(7, -10)
print(Vector2.PolarString(a, b))
print("=================================================\n")

d = Vector2(0, 0)
d.SetMagnitudeAndDirection(40, 180)

# TODO: PolarString does not properly determine the quadrant the angle must be in and therefore returns a numerically reduced angle,
#       which is incorrect!
print(d.ToPolarString()) # This returns 9.7 (10) which is the numerically reduced form of 170deg

v3 = Vector3(10, 0, -1)
v4 = Vector3(-10, 0, 1)
print(f"Distance between vector v1 and v2: {Vector3.Distance(v3, v4)}")
print(v4[0])
print(v3)   # This uses the overloaded implicit string conversion operator.

print("=====================================================================\n\n\n\n")

values = [10, 990, 1024.28, 602.4, 44, 556.7, 90,54, 0.0076, 99.23]
print(f"MIN: {Mathf.Min(values)}")
print(f"MAX: {Mathf.Max(values)}")
