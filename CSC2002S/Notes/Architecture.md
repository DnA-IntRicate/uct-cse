# Architecture Notes

## Dennard Scaling (MOSFET Scaling)

#### Brief
The observation that as circuits become smaller and faster, power density remains the same.

---

## Clock Cycles

### Cycles Per Instruction (CPI)

``` math
CPI = \frac{TotalClockCycles}{NumberOfInstructions}
```

``` math
CPU \; Time = Instructions \times CPI \times ClockCycleTime
```

``` math
CPU \; Time = \frac{Instructions \times CPI}{ClockFrequency}
```

---

## Cache Mapping

``` math
CacheIndex = MemoryBlockNumber \pmod{NumberOfCacheBlocks}
```

``` math
MemoryBlockNumber = \lfloor \frac{MemoryAddress}{BlockSize} \rfloor
```

---

## MIPS Branch Addressing (I-Type)

``` math
TargetAddr = (PC + 4) + (signextend(Offset) \times 4) \\
TargetAddr = (PC + 100_{2}) + (Ext_{32}(Offset) \ll 2_{10})
```

#### Where:
- **Offset**: i16 value (PC-relative)
- **$\times 4 \;(\ll 2)$**: Scaling factor

#### Brief:
1. Sign-extend the **Offset** to `32` bits.
2. Shift left by `2` bits.
3. Add to $PC + 4$.

**NOTE**: The last `16` bits of the instruction is the **offset address**

---

## MIPS Jump Addressing (J-Type)

``` math
TargetAddr = Upper_4(PC + 4) \;|\; (Offset \ll 2)
```

#### Where:
- **Offset**: i26 value (pseudo-absolute)

## Endianness

- **Big Endian**: MSB is first.
- **Little Endian**: LSB is first (the one used by **AMD64** and **ARM**)

---
