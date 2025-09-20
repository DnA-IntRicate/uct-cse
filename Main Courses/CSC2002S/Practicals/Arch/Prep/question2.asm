.globl main

.data
    SYS_WRITE:      .byte 4
    SYS_WRITE_INT:  .byte 1
    SYS_READ_INT:   .byte 5
    SYS_EXIT:       .byte 10

    NEWLINE:        .asciiz "\n"
    PROMPT1:        .asciiz "Enter coordinate one (x1,y2):\n"
    PROMPT2:        .asciiz "Enter coordinate two (x2,y2):\n"
    PROMPT3:        .asciiz "The distance is:\n"

.text
    # $a0 = String address
    Print:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_WRITE
        syscall

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    # $a0 = Integer to print
    PrintInt:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_WRITE_INT
        syscall

        la      $a0, NEWLINE
        jal     Print

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    # Returns $v0
    ReadInt:
        lb      $v0, SYS_READ_INT
        syscall
        jr      $ra
        nop

    # $a0 = Integer to compute the square root of
    # Returns $v0
    Sqrt:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        move    $t0, $a0        # $t0 = x = n ($a0)
        xor     $t1, $t1, $t1   # $t1 = i = 0
        li      $t2, 2          # $t2 = 2
        div     $t0, $t2
        mflo    $t3             # $t3 = bound = n / 2
        j       SqrtLoop

        SqrtLoop:
            bge     $t1, $t3, BreakSqrtLoop
            div     $a0, $t0        # n / x
            mflo    $t4             # $t4 = n / x
            add     $t5, $t0, $t4   # $t5 = x + (n / x)
            div     $t5, $t2        # $t5 / 2
            mflo    $t0             # $t0 = x = (x + (n / x)) / 2
            addi    $t1, $t1, 1
            j       SqrtLoop

        BreakSqrtLoop:
            lw      $ra, 0($sp)
            addi    $sp, $sp, 4
            move    $v0, $t0        # Return x ($t0)
            jr      $ra
            nop

    # $a0 = x1, $a1 = y1
    # $a2 = x2, $a3 = y2
    # Returns $v0
    Distance:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        sub     $t0, $a2, $a0   # $t0 = x2 - x1
        mul     $t0, $t0, $t0   # Square $t0
        sub     $t1, $a3, $a1   # $t1 = y2 - y1
        mul     $t1, $t1, $t1   # Square $t1
        add     $t2, $t0, $t1   # $t2 = $t0 + $t1

        move    $a0, $t2
        jal     Sqrt

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    main:
        la      $a0, PROMPT1
        jal     Print
        jal     ReadInt
        move    $t0, $v0
        jal     ReadInt
        move    $t1, $v0

        la      $a0, PROMPT2
        jal     Print
        jal     ReadInt
        move    $t2, $v0
        jal     ReadInt
        move    $t3, $v0

        move    $a0, $t0
        move    $a1, $t1
        move    $a2, $t2
        move    $a3, $t3
        jal     Distance
        move    $t4, $v0

        la      $a0, PROMPT3
        jal     Print
        move    $a0, $t4
        jal     PrintInt

        j       Exit

    Exit:
        lb      $v0, SYS_EXIT
        syscall
