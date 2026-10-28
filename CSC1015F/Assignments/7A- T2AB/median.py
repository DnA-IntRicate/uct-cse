def median_value(value_a, value_b, value_c):
    min = value_a
    mid = value_b
    max = value_c
    if min > mid:
        min = value_b
        mid = value_a
    if mid > max:
        max = mid
        mid = value_c
        if min > mid:
            mid = min
            min = value_c
    return mid
