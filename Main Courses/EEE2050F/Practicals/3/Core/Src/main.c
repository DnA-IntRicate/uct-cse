// Adam Foflonker
// FFLADA001
// 27 April 2026

#include <main.h>
#include <lcd_stm32f0.h>
#include "stm32f0xx.h"

#define TRUE 1
#define FALSE 0

#define LED_COUNT 8
#define BUTTON_COUNT 4

#define DELAY1 2000
#define DELAY2 400

// TODO: Figure out what the fuck to define these as
#define BITPATTERN1
#define BITPATTERN2
#define BITPATTERN3

//====================================================================
// GLOBAL VARIABLES
//====================================================================

typedef uint8_t flag_t;

volatile flag_t g_start_flag = FALSE;
volatile flag_t g_first_flag = FALSE;
volatile flag_t g_second_flag = FALSE;
volatile flag_t g_third_flag = FALSE;

void init_clock(void);
void init_gpio(void);
void my_delay(void); // NOTE: 'delay' is already defined in lcd_stm32f0.h

void write_leds(uint8_t pattern);
void first_display(void);
void second_display(void);
void third_display(void);

void check_pb(void);
void display(void);

int main(void)
{
    // Do not delete: Initializes system clock to correct configuration
    init_clock();

    init_gpio();

    // LCD print
    init_LCD();
    lcd_command(CLEAR | TWOLINE_MODE);
    lcd_putstring("EEE2046 Prac3");
    lcd_command(LINE_TWO);
    lcd_putstring("By Adam");

    // Switch on LED D0
    GPIOB->BSRR = (1 << 0); // TODO: Keep this on for a short duration then turn it off
    g_start_flag = TRUE;

    while (TRUE)
    {
        check_pb();
        display();
    }
}

void init_clock(void)
{
    // 1. Enable HSE
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY))
        ;

    // 2. Configure Flash latency for 48 MHz
    FLASH->ACR |= FLASH_ACR_LATENCY;

    // 3. Set PREDIV = / 2 (HSE / 2)
    RCC->CFGR2 &= ~RCC_CFGR2_PREDIV;
    RCC->CFGR2 |= RCC_CFGR2_PREDIV_DIV2;

    // 4. Configure PLL
    // Source = HSE/PREDIV
    RCC->CFGR &= ~RCC_CFGR_PLLSRC;
    RCC->CFGR |= RCC_CFGR_PLLSRC_HSE_PREDIV;

    // Set PLL multiplier = x12
    RCC->CFGR &= ~RCC_CFGR_PLLMUL;
    RCC->CFGR |= RCC_CFGR_PLLMUL12;

    // 5. Enable PLL
    RCC->CR |= RCC_CR_PLLON;
    while (!(RCC->CR & RCC_CR_PLLRDY))
        ;

    // 6. Set AHB prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_HPRE;

    // 7. Set APB prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_PPRE;

    // 8. Select PLL as system clock
    RCC->CFGR &= ~RCC_CFGR_SW;
    RCC->CFGR |= RCC_CFGR_SW_PLL;

    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL)
        ;
}

void init_gpio(void)
{
    // Enable clocks for GPIOA (buttons) and GPIOB (LEDs)
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

    // Initialize GPIOA (buttons) as input with pull-up
    // PA0 - PA3
    for (int pin = 0; pin < BUTTON_COUNT; ++pin)
    {
        // Input mode
        GPIOA->MODER &= ~(3 << (pin * 2));

        // Pull-up
        GPIOA->PUPDR &= ~(3 << (pin * 2));
        GPIOA->PUPDR |= (1 << (pin * 2));
    }

    // Initialize GPIOB (LEDs) as outputs
    // PB0 - PB7
    for (int pin = 0; pin < LED_COUNT; ++pin)
    {
        // Output mode
        GPIOB->MODER &= ~(3 << (pin * 2));
        GPIOB->MODER |= (1 << (pin * 2));

        // Push-pull
        GPIOB->OTYPER &= ~(1 << pin);

        // High speed
        GPIOB->OSPEEDR |= (3 << (pin * 2));

        // No pull-up/down
        GPIOB->PUPDR &= ~(3 << (pin * 2));
    }
}

void my_delay(void)
{
    volatile int i, j;
    for (i = 0; i < DELAY2; ++i)
    {
        for (j = 0; j < DELAY1; ++j)
        {
            check_pb();
            __asm__ volatile("nop");
        }
    }
}

void write_leds(uint8_t pattern)
{
    // Clear all LEDs
    GPIOB->BRR = UINT8_MAX;
    GPIOB->BSRR = pattern;
}

void first_display(void)
{
    while (g_first_flag)
    {
        // TODO: This must show the bitpatterns!

        write_leds(1 << 0);
        my_delay();

        if (!g_first_flag)
            break;

        write_leds(1 << 1);
        my_delay();

        if (!g_first_flag)
            break;

        write_leds(1 << 2);
        my_delay();
    }
}

void second_display(void)
{
    while (g_second_flag)
    {
        for (int led = 0; led < LED_COUNT; ++led)
        {
            if (!g_second_flag)
                break;

            write_leds(1 << led);
            my_delay();
        }
    }
}

void third_display(void)
{
    uint8_t counter = 0;
    while (g_third_flag)
    {
        write_leds(counter);
        counter++;
        my_delay();
    }
}

void check_pb(void)
{
    // Read buttons
    int btn0 = (GPIOA->IDR & (1 << 0)) == FALSE;
    int btn1 = (GPIOA->IDR & (1 << 1)) == FALSE;
    int btn2 = (GPIOA->IDR & (1 << 2)) == FALSE;

    if (btn0)
    {
        g_start_flag = FALSE;
        g_first_flag = TRUE;
        g_second_flag = FALSE;
        g_third_flag = FALSE;
    }
    else if (btn1)
    {
        g_start_flag = FALSE;
        g_first_flag = FALSE;
        g_second_flag = TRUE;
        g_third_flag = FALSE;
    }
    else if (btn2)
    {
        g_start_flag = FALSE;
        g_first_flag = FALSE;
        g_second_flag = FALSE;
        g_third_flag = TRUE;
    }
}

void display(void)
{
    if (g_start_flag)
        return;

    if (g_first_flag)
        first_display();
    else if (g_second_flag)
        second_display();
    else if (g_third_flag)
        third_display();
}
