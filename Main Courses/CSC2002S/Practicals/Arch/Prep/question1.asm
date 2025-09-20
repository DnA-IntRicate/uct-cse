.globl main

.data
    SYS_WRITE_INT:  .byte 1
    SYS_WRITE:      .byte 4
    SYS_READ_INT:   .byte 5
    SYS_READ:       .byte 8
    SYS_EXIT:       .byte 10

    NEWLINE:        .asciiz "\n"
    PROMPT1:        .asciiz "Enter a number:\n"
    PROMPT2:        .asciiz "The Fibonacci number is:\n"

.text
    # $a0: String address
    Print:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_WRITE
        syscall

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    # Returns: $v0
    ReadInt:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_READ_INT
        syscall

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    # $a0: Integer to print
    PrintInt:
        addi    $sp, $sp -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_WRITE_INT
        syscall

        la      $a0, NEWLINE
        jal     Print

        lw      $ra, 0($sp)
        addi    $sp, $sp, 4
        jr      $ra
        nop

    # $a0: n
    # Returns: $v0
    Fib:
        addi    $sp, $sp, 4
        sw      $ra, 0($sp)

        ble     $a0, 0, LessThanOrEqZero
        beq     $a0, 1, One

        li      $t0, 0  # Fib(0)
        li      $t1, 1  # Fib(1)
        li      $t2, 2  # i = 2

        Loop:
            bgt     $t2, $a0, BreakLoop
            add     $t3, $t0, $t1
            move    $t0, $t1
            move    $t1, $t3
            addi    $t2, $t2, 1
            j       Loop

        BreakLoop:
            move    $v0, $t1

            lw      $ra, 0($sp)
            addi    $sp, $sp, 4
            jr      $ra
            nop

        LessThanOrEqZero:
            li      $v0, 0

            lw      $ra, 0($sp)
            addi    $sp, $sp, 4
            jr      $ra
            nop

        One:
            li      $v0, 1

            lw      $ra, 0($sp)
            addi    $sp, $sp, 4
            jr      $ra
            nop

    main:
        la      $a0, PROMPT1
        jal     Print
        jal     ReadInt

        move    $a0, $v0
        jal     Fib
        move    $t0, $v0

        la      $a0, PROMPT2
        jal     Print

        move    $a0, $t0
        jal     PrintInt
        j       Exit

    Exit:
        lb      $v0, SYS_EXIT
        syscall
