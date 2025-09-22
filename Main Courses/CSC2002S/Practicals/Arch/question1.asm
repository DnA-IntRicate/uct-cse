.globl main

.data
    SYS_WRITE_INT:  .byte 1
    SYS_WRITE:      .byte 4
    SYS_READ_INT:   .byte 5
    SYS_READ_CHAR:  .byte 12
    SYS_READ:       .byte 8
    SYS_EXIT:       .byte 10

    OP_ADD:         .byte 43 # '+'
    OP_SUB:         .byte 45 # '-'
    OP_MUL:         .byte 42 # '*'
    OP_DIV:         .byte 47 # '/'

    NEWLINE:        .asciiz "\n"

.text
    # $a0: String address
    Print:
        addi    $sp, $sp, -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_WRITE
        syscall

        lw      $ra 0($sp)
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

    # Returns: $v0
    ReadChar:
        addi    $sp, $sp -4
        sw      $ra, 0($sp)

        lb      $v0, SYS_READ_CHAR
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

    main:
        jal     ReadInt
        move    $t0, $v0    # $t0 = a

        jal     ReadChar
        move    $t1, $v0    # $t1 = op
        jal     ReadChar    # Read the trailing newline

        jal     ReadInt
        move    $t2, $v0    # $t2 = b

        # $t3 = Result
        xor     $t3, $t3, $t3

        lb      $t4, OP_ADD
        beq     $t1, $t4, Add
        lb      $t4, OP_SUB
        beq     $t1, $t4, Sub
        lb      $t4, OP_MUL
        beq     $t1, $t4, Mul
        lb      $t4, OP_DIV
        beq     $t1, $t4, Div

        Add:
            add     $t3, $t0, $t2
            j       End

        Sub:
            sub     $t3, $t0, $t2
            j       End

        Mul:
            mul     $t3, $t0, $t2
            j       End

        Div:
            div     $t0, $t2
            mflo    $t3
            j       End

        End:
            move    $a0, $t3
            jal     PrintInt
            j       Exit

    Exit:
        lb      $v0, SYS_EXIT
        syscall
