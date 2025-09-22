.globl main

.data
    SYS_WRITE_INT:  .byte 1
    SYS_WRITE:      .byte 4
    SYS_READ_INT:   .byte 5
    SYS_READ:       .byte 8
    SYS_EXIT:       .byte 10

    NEWLINE:        .asciiz "\n"

    stackOffset:    .word 0

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
        move    $t0, $sp    # Store pointer to the base of the stack in $t0

        ReadLoop:
            jal     ReadInt
            beq     $v0, $zero, BreakReadLoop

            addi    $sp, $sp, -4
            sw      $v0, stackOffset($sp)
            lw      $t1, stackOffset    # Add 4 to stackOffset
            addi    $t1, $t1, 4
            sw      $t1, stackOffset

            j       ReadLoop

        BreakReadLoop:
            sw      $zero, stackOffset
            j       ReversePrintNumbers

        ReversePrintNumbers:
            beq     $t0, $sp, DonePrinting
            lw      $a0, stackOffset($sp)
            jal     PrintInt

            addi    $sp, $sp, 4
            j       ReversePrintNumbers

        DonePrinting:
            j       Exit

    Exit:
        lb      $v0, SYS_EXIT
        syscall
