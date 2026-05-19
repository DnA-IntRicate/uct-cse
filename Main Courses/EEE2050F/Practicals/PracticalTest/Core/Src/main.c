// Adam Foflonker
// FFLADA001
// 19 May 2026
// EEE2050F: Practical Test

#include <main.h>
#include <lcd_stm32f0.h>
#include "stm32f0xx.h"

#define TRUE 1
#define FALSE 0

#define DELAY1 400000
#define DELAY2 1000

typedef uint8_t flag_t;
flag_t g_start_flag = FALSE;
flag_t g_reset_state = TRUE;

uint8_t g_count = 1;

void init_gpio(void);
void delay_1s(void);
void check_pb(void);
void counter(void);
void display(void);

// Utils
void write_leds(uint8_t pattern);

int main(void)
{
    // Splash screen
    init_LCD();
    lcd_command(TWOLINE_MODE | CLEAR);
    lcd_putstring("EEE2050F (PT)");
    lcd_command(LINE_TWO);
    lcd_putstring("Foflonker");

    // Init GPIO
    init_gpio();

    while (TRUE)
    {
        check_pb();
        display();

        // Q6: Testing delay_1s()
        // GPIOB->ODR ^= UINT8_MAX;
        // delay_1s();

        // Q7: Testing check_pb()
        // if (g_start_flag)
        //     write_leds(0);
        // else
        //     write_leds(UINT8_MAX);

        // Q8: Testing counter()
        // counter();
        // write_leds(g_count);
    }
}

void init_gpio(void)
{
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

    // PA0 and PA1 as inputs
    GPIOA->MODER &= ~(3 << 0) | (3 << 2); // Input
    GPIOA->PUPDR &= ~(3 << 0) | (3 << 2);
    GPIOA->PUPDR |= (1 << 0) | (1 << 2); // Pull-up

    // PB0 - PB7 as outputs
    GPIOB->MODER &= ~(((uint16_t)-1) << 0);
    GPIOB->MODER |= (1 << 0) | (1 << 2) | (1 << 4) | (1 << 6) | (1 << 8) | (1 << 10) | (1 << 12) | (1 << 14); // Output
    GPIOB->PUPDR &= ~(((uint16_t)-1) << 0); // Disable pull-up pull-down

    // Test all LEDs
    // GPIOB->BSRR = UINT8_MAX;

    // Display initial g_count
    write_leds(g_count);
}

void delay_1s(void)
{
    volatile int i = 0, j = 0;
    for (; i < DELAY1; ++i)
    {
        for (; j < DELAY2; ++j)
        {
            check_pb();
            __asm__ ("nop");
        }
    }
}

void check_pb(void)
{
    int btn0 = (GPIOA->IDR & GPIO_IDR_0) == 0;
    int btn1 = (GPIOA->IDR & GPIO_IDR_1) == 0;

    if (btn0)
    {
        g_start_flag = TRUE;
        g_reset_state = FALSE;
        lcd_command(CLEAR);
    }
    else if (btn1)
    {
        g_start_flag = FALSE;
        g_reset_state = FALSE;
        lcd_command(CLEAR);
    }
}

void counter(void)
{
    delay_1s();
    g_count += 2;
}

void display(void)
{
    if (g_reset_state)
        return;

    if (g_start_flag)
    {
        lcd_putstring("Counter");
        lcd_command(LINE_TWO);
        lcd_putstring("Started");
        lcd_command(CURSOR_HOME);

        counter();
        write_leds(g_count);
    }
    else
    {
        lcd_putstring("Counter");
        lcd_command(LINE_TWO);
        lcd_putstring("Stopped");
        lcd_command(CURSOR_HOME);
    }
}

void write_leds(uint8_t pattern)
{
    GPIOB->BRR = UINT8_MAX;
    GPIOB->BSRR = pattern;
}
