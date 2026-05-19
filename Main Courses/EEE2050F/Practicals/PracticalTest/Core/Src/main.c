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
flag_t startFlag = FALSE;
flag_t resetState = TRUE;
uint8_t count = 1;

void initGPIO(void);
void delay_1s(void);
void checkPB(void);
void counter(void);
void display(void);

// Utils
void write_leds(uint8_t pattern);

int main(void)
{
    // Initializes system clock to correct configuration
    // init_clock();

    // Splash screen
    init_LCD();
    lcd_command(TWOLINE_MODE | CLEAR);
    lcd_putstring("EEE2050F (PT)");
    lcd_command(LINE_TWO);
    lcd_putstring("Foflonker");

    // Init GPIO
    initGPIO();

    while (TRUE)
    {
        checkPB();
        display();

        // Q6: Testing delay_1s()
        // GPIOB->ODR ^= UINT8_MAX;
        // delay_1s();

        // Q7: Testing checkPB()
        // if (startFlag)
        //     write_leds(0);
        // else
        //     write_leds(UINT8_MAX);

        // Q8: Testing counter()
        // counter();
        // write_leds(count);
    }
}

void initGPIO(void)
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

    // Display initial count
    write_leds(count);
}

void delay_1s(void)
{
    volatile int i = 0, j = 0;
    for (; i < DELAY1; ++i)
    {
        for (; j < DELAY2; ++j)
        {
            checkPB();
            __asm__ ("nop");
        }
    }
}

void checkPB(void)
{
    int btn0 = (GPIOA->IDR & GPIO_IDR_0) == 0;
    int btn1 = (GPIOA->IDR & GPIO_IDR_1) == 0;

    if (btn0)
    {
        startFlag = TRUE;
        resetState = FALSE;
        lcd_command(CLEAR);
    }
    else if (btn1)
    {
        startFlag = FALSE;
        resetState = FALSE;
        lcd_command(CLEAR);
    }
}

void counter(void)
{
    delay_1s();
    count += 2;
}

void display(void)
{
    if (resetState)
        return;

    if (startFlag)
    {
        lcd_putstring("Counter");
        lcd_command(LINE_TWO);
        lcd_putstring("Started");
        lcd_command(CURSOR_HOME);

        counter();
        write_leds(count);
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
