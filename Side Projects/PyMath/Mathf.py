import math

class Mathf:
    @staticmethod
    def Abs(value: float) -> float:
        return abs(value)

    @staticmethod
    def Min(values: list) -> float:
        if len(values) == 0:
            return 0.0

        res = values[0]
        for v in values:
            if v < res:
                res = v

        return res

    @staticmethod
    def Max(values: list) -> float:
        if len(values) == 0:
            return 0.0

        res = values[0]
        for v in values:
            if v > res:
                res = v

        return res

    @staticmethod
    def Clamp(value: float, min: float, max: float) -> float:
        if (value < min):
            return min
        elif (value > max):
            return max

        return value;

    @staticmethod
    def Clamp01(value: float) -> float:
        if (value < 0.0):
            return 0.0
        elif (value > 1.0):
            return 1.0

        return value;

    @staticmethod
    def Lerp(a: float, b: float, interpolant: float) -> float:
        return a + (b - a) * Mathf.Clamp01(interpolant)

    @staticmethod
    def LerpUnclamped(a: float, b: float, interpolant: float) -> float:
        return a + (b - a) * interpolant
