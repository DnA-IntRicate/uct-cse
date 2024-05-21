import math

def InvertBits(bits: str) -> str:
    res = ""
    for bit in bits:
        res += "1" if (bit == "0") else "0"

    return res

def IntToBinary(n: int) -> str:
    if n == 0:
        return "0"

    res = ""

    i = abs(n)
    while i >= 1:
        res += str(i % 2)
        i //= 2

    return ("-" if n < 0 else "") + res[::-1]

def FloatToBinary(n: float, bits: int = 32) -> str:
    frac, whole = math.modf(abs(n))
    wholeBinary = IntToBinary(int(whole))

    fracBinary = ""
    while frac > 0.0:
        fracBinary += str(int(frac * 2.0))
        frac = math.modf(frac * 2.0)[0]

        if (len(fracBinary) + len(wholeBinary)) >= bits:
            fracBinary = fracBinary[:bits - len(wholeBinary)]

    return f"{wholeBinary}.{fracBinary}"

def DecimalToBinarySigned2sComplement(n: int, bits: int = 8) -> str:
    sign = "1" if n < 0 else "0"
    binary = IntToBinary(abs(n))
    lastBit = binary[-1]

    if sign == "1":
        binary = InvertBits(binary)

    return (sign + binary[:-1] + lastBit).rjust(bits, sign)

def FloatToBinary32(n: float) -> str:
    sign = "1" if n < 0 else "0"
    binary = FloatToBinary(abs(n), 32)

    posDot = binary.find('.')
    posFirstOne = binary.find('1')
    mantissa = binary.replace('.', '')[posFirstOne + 1:][:23]
    exponent = IntToBinary(127 + (posDot - 1))

    return sign + exponent + mantissa.ljust(23, '0')
