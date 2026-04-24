// Adam Foflonker
// FFLADA001
// 24 April 2026

#include "stm32f0xx.h"
#include <lcd_stm32f0.h>

#define TRUE 1
#define FALSE 0
#define NULLPTR ((void*)0)

// Delay macros (tune values for 1s at 48MHz)
#define DELAY1 1000
#define DELAY2 1000

// Interruptible delays
#define DELAY_STEPS 100
#define DELAY_CHUNK (DELAY1 * DELAY2 / DELAY_STEPS)

// Bit patterns for LEDs on PB0-PB7, PB10-PB11
#define BIT_PATTERN_1 0x00000055 // PB0, PB2, PB4, PB6
#define BIT_PATTERN_2 0x000000AA // PB1, PB3, PB5, PB7
#define BIT_PATTERN_3 0x00000C00 // PB10, PB11

typedef uint8_t flag_t;

flag_t g_start_flag = FALSE;
flag_t g_first_flag = FALSE;
flag_t g_second_flag = FALSE;
flag_t g_third_flag = FALSE;

// Forward declarations
void init_clock(void);
void init_gpio(void);
void my_delay_blocking(void);
void my_delay(flag_t* flag);    // 'delay' is already defined in lcd_stm32f0.h
void first_display(void);
void second_display(void);
void third_display(void);
void check_pb(void);
void display(void);

int main(void)
{
    // TODO: Investigate why clock initialization is interfering with our delay logic
    // init_clock();
    init_gpio();

    // Switch on D0 briefly as startup indicator
    GPIOB->BSRR = (1 << 0);
    my_delay_blocking();

    // All LEDs OFF
    GPIOB->BRR = 0x00000CFF;

    // Wait until SW0 is explicitly pressed and released
    while (GPIOA->IDR & (1 << 0)); // Wait for press (LOW)
    while (!(GPIOA->IDR & (1 << 0))); // Wait for release (HIGH)

    g_start_flag = TRUE;
    while (TRUE)
    {
        check_pb();
        display();
    }
}

void init_gpio(void)
{
    // Enable clocks for GPIOA (buttons) and GPIOB (LEDs)
    RCC->AHBENR |= (1 << 17); // IOPAEN - GPIOA
    RCC->AHBENR |= (1 << 18); // IOPBEN - GPIOB

    // Set MODER to 01 (output) for PB0-PB7, PB10-PB11
    GPIOB->MODER |= 0x00505555;

    // Push-pull output type (default, but explicit)
    GPIOB->OTYPER &= ~0x00000CFF;

    // Low speed (default, but explicit)
    GPIOB->OSPEEDR &= ~0x00F0FFFF;

    // No pull-up/pull-down for outputs
    GPIOB->PUPDR &= ~0x00F0FFFF;

    // --- Buttons on PA0-PA3 as inputs ---
    // MODER = 00 (input) for PA0-PA3 (default, but explicit)
    GPIOA->MODER &= ~0x000000FF;

    // No pull (external resistors on board handle this)
    GPIOA->PUPDR &= ~0x000000FF;
}

void my_delay_blocking(void)
{
    for (int i = 0; i < DELAY1; ++i)
    {
        for (volatile int j = 0; j < DELAY2; ++j)
            __NOP();
    }
}

void my_delay(flag_t* flag)
{
    for (int s = 0; s < DELAY_STEPS; ++s)
    {
        for (volatile int i = 0; i < DELAY_CHUNK; ++i)
            __NOP();

        check_pb();
        if (!(*flag))
            return; // Exit early if flag cleared
    }
}

void first_display(void)
{
    while (g_first_flag)
    {
        GPIOB->ODR = BIT_PATTERN_1;
        my_delay(&g_first_flag);

        if (!g_first_flag)
            break;

        GPIOB->ODR = BIT_PATTERN_2;
        my_delay(&g_first_flag);

        if (!g_first_flag)
            break;

        GPIOB->ODR = BIT_PATTERN_3;
        my_delay(&g_first_flag);
    }
}

void second_display(void)
{
    while (g_second_flag)
    {
        for (int i = 0; i < 8; ++i)
        {
            GPIOB->ODR = (1 << i);
            my_delay(&g_second_flag);

            if (!g_second_flag)
                return;
        }
    }
}

void third_display(void)
{
    while (g_third_flag)
    {
        for (int i = 0; i < 256; ++i)
        {
            GPIOB->ODR = i;
            my_delay(&g_third_flag);

            if (!g_third_flag)
                return;
        }
    }
}

void check_pb(void)
{
    uint16_t pb = GPIOA->IDR & 0x000F;

    if (!(pb & (1 << 1))) // SW1
    {
        g_first_flag = TRUE;
        g_second_flag = FALSE;
        g_third_flag = FALSE;
    }

    if (!(pb & (1 << 2))) // SW2
    {
        g_first_flag = FALSE;
        g_second_flag = TRUE;
        g_third_flag = FALSE;
    }

    if (!(pb & (1 << 3))) // SW3
    {
        g_first_flag = FALSE;
        g_second_flag = FALSE;
        g_third_flag = TRUE;
    }
}

void display(void)
{
    if (g_first_flag)
        first_display();
    else if (g_second_flag)
        second_display();
    else if (g_third_flag)
        third_display();
}

void init_clock(void)
{
    // 1. Enable HSE
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY));

    // 2. Configure Flash latency for 48 MHz
    FLASH->ACR |= FLASH_ACR_LATENCY;

    // 3. Set PREDIV = ÷2 (HSE / 2)
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
    while (!(RCC->CR & RCC_CR_PLLRDY));

    // 6. Set AHB prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_HPRE;

    // 7. Set APB prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_PPRE;

    // 8. Select PLL as system clock
    RCC->CFGR &= ~RCC_CFGR_SW;
    RCC->CFGR |= RCC_CFGR_SW_PLL;

    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL);
}
