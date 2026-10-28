//********************************************************************
//*                    EEE2046F C template                           *
//*==================================================================*
//* WRITTEN BY: Jesse Arendse   	                 		               *
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

//====================================================================
// GLOBAL VARIABLES
//====================================================================

//====================================================================
// FUNCTION DECLARATIONS
//====================================================================
void init_clock();
void helloWorld();
//====================================================================
// MAIN FUNCTION
//====================================================================
int main (void)
{
    //Do not delete: Initializes system clock to correct configuration
    init_clock();
    
    helloWorld();
    while(1){

    }
}							// End of main

//====================================================================
// FUNCTION DEFINITIONS
//====================================================================

void helloWorld(){
    init_LCD();
    lcd_command(CLEAR);
    lcd_putstring("Hello World! :)");
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
