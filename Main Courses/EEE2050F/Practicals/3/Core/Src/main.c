//********************************************************************
//*                    EEE2046F C template                           *
//*==================================================================*
//* WRITTEN BY: Jesse Arendse   	                 		         *
//* DATE CREATED: 07/04/2023                                         *
//* MODIFIED:                                                        *
//*==================================================================*
//* PROGRAMMED IN: Visual Studio Code                                *
//* TARGET:        STM32F0                                           *
//*==================================================================*
//* DESCRIPTION:                                                     *
//*                                                                  *
//********************************************************************
// INCLUDE FILES
//====================================================================
#include "stm32f0xx.h"
#include <lcd_stm32f0.h>
//====================================================================
// GLOBAL CONSTANTS
//====================================================================
#define TRUE 1
#define FALSE 0

// Delay macros (tune values for 1s at 48MHz)
#define DELAY1 1000
#define DELAY2 1000

// Bit patterns for LEDs on PB0-PB7, PB10-PB11
// (adjust these to your desired patterns)
#define bitpattern1 0x00000055 // PB0, PB2, PB4, PB6
#define bitpattern2 0x000000AA // PB1, PB3, PB5, PB7
#define bitpattern3 0x00000C00 // PB10, PB11
//====================================================================
// GLOBAL VARIABLES
//====================================================================
typedef uint8_t flag_t;

flag_t startFlag = FALSE;
flag_t firstFlag = FALSE;
flag_t secondFlag = FALSE;
flag_t thirdFlag = FALSE;
//====================================================================
// FUNCTION DECLARATIONS
//====================================================================
void init_clock(void);

void init_gpio(void);
void my_delay(void);    // 'delay' is already defined in lcd_stm32f0.h
void firstDisplay(void);
void secondDisplay(void);
void thirdDisplay(void);
void checkPB(void);
void display(void);
//====================================================================
// MAIN FUNCTION
//====================================================================
int main(void)
{
    init_clock();
    init_gpio();

    // Switch on D0 briefly as startup indicator
    GPIOB->BSRR = (1 << 0);
    my_delay();

    // All LEDs OFF
    GPIOB->BRR = 0x00000CFF;

    // Wait until SW0 is explicitly pressed and released
    while (GPIOA->IDR & (1 << 0)); // Wait for press (goes LOW)
    while (!(GPIOA->IDR & (1 << 0))); // Wait for release (goes HIGH)

    startFlag = TRUE;
    while (1)
    {
        checkPB();
        display();
    }
}

//====================================================================
// FUNCTION DEFINITIONS
//====================================================================

void init_gpio(void)
{
    // Enable clocks for GPIOA (buttons) and GPIOB (LEDs)
    RCC->AHBENR |= (1 << 17); // IOPAEN - GPIOA
    RCC->AHBENR |= (1 << 18); // IOPBEN - GPIOB

    // --- LEDs on PB0-PB7, PB10-PB11 as outputs ---
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

void my_delay(void)
{
    for (volatile int i = 0; i < DELAY1; i++)
    {
        for (volatile int j = 0; j < DELAY2; j++)
        {
            __NOP();
        }
    }
}

void firstDisplay(void)
{
    // Cycle through 3 patterns with 1s delay, repeat
    while (firstFlag)
    {
        GPIOB->ODR = bitpattern1;
        my_delay();
        GPIOB->ODR = bitpattern2;
        my_delay();
        GPIOB->ODR = bitpattern3;
        my_delay();
        checkPB(); // Check buttons during display
    }
}

void secondDisplay(void)
{
    // 8-step LED chase on PB0-PB7, repeat
    while (secondFlag)
    {
        for (int i = 0; i < 8; i++)
        {
            GPIOB->ODR = (1 << i);
            my_delay();
        }
        checkPB(); // Check buttons during display
    }
}

void thirdDisplay(void)
{
    // 8-bit binary counter on PB0-PB7, repeat
    while (thirdFlag)
    {
        for (int i = 0; i < 256; i++)
        {
            GPIOB->ODR = i;
            my_delay();
        }
        checkPB(); // Check buttons during display
    }
}

void checkPB(void)
{
    uint16_t pb = GPIOA->IDR & 0x000F;

    if (!(pb & (1 << 1))) // SW1
    {
        firstFlag = TRUE;
        secondFlag = FALSE;
        thirdFlag = FALSE;
    }

    if (!(pb & (1 << 2))) // SW2
    {
        firstFlag = FALSE;
        secondFlag = TRUE;
        thirdFlag = FALSE;
    }

    if (!(pb & (1 << 3))) // SW3
    {
        firstFlag = FALSE;
        secondFlag = FALSE;
        thirdFlag = TRUE;
    }
}

void display(void)
{
    if (firstFlag)
        firstDisplay();
    else if (secondFlag)
        secondDisplay();
    else if (thirdFlag)
        thirdDisplay();
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
//********************************************************************
// END OF PROGRAM
//********************************************************************
