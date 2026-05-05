// Adam Foflonker
// FFLADA001
// 05 May 2026

#include <main.h>
#include <lcd_stm32f0.h>
#include "stm32f0xx.h"


#define TRUE 1
#define FALSE 0

void init_clock(void);
void init_gpio(void);
void init_timer(void);

void write_leds(uint8_t pattern);

void check_pb(void);

int main(void)
{
    // Do not delete: Initializes system clock to correct configuration
    init_clock();

    // Initialize all buttons and LEDs
    init_gpio();

    // Initialize TIM14
    init_timer();

    // Splash screen
    init_LCD();
    lcd_command(CLEAR | TWOLINE_MODE);
    lcd_putstring("EEE2046 Prac 4");
    lcd_command(LINE_TWO);
    lcd_putstring("~ By Adam");

    while (TRUE)
    {
        check_pb();

        // if (g_start_flag)
        // {
        //     lcd_command(CLEAR);
        //     lcd_putstring("Ready to start");
        //     write_leds(1 << 0);

        //     g_start_flag = FALSE; // Reset state since start doesn't require any continuous logic
        // }
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
    // PA0 - PA2
    {
        GPIOA->MODER &= ~(GPIO_MODER_MODER0 | GPIO_MODER_MODER1 | GPIO_MODER_MODER2); // Input mode

        // Pull-up
        GPIOA->PUPDR &= ~(GPIO_PUPDR_PUPDR0 | GPIO_PUPDR_PUPDR1 | GPIO_PUPDR_PUPDR2);
        GPIOA->PUPDR |= GPIO_PUPDR_PUPDR0_0 | GPIO_PUPDR_PUPDR1_0 | GPIO_PUPDR_PUPDR2_0;
    }

    // Initialize GPIOB (LEDs) as outputs
    // PB0 - PB7
    {
        GPIOB->MODER &= ~(GPIO_MODER_MODER0 | GPIO_MODER_MODER1 | GPIO_MODER_MODER2 | GPIO_MODER_MODER3 | GPIO_MODER_MODER4
                | GPIO_MODER_MODER5 | GPIO_MODER_MODER6 | GPIO_MODER_MODER7);
        GPIOB->MODER |= GPIO_MODER_MODER0_0 | GPIO_MODER_MODER1_0 | GPIO_MODER_MODER2_0 | GPIO_MODER_MODER3_0 | GPIO_MODER_MODER4_0
            | GPIO_MODER_MODER5_0 | GPIO_MODER_MODER6_0 | GPIO_MODER_MODER7_0; // Output mode

        // Push-pull output
        GPIOB->OTYPER &= ~(GPIO_OTYPER_OT_0 | GPIO_OTYPER_OT_1 | GPIO_OTYPER_OT_2 | GPIO_OTYPER_OT_3 | GPIO_OTYPER_OT_4
                | GPIO_OTYPER_OT_5 | GPIO_OTYPER_OT_6 | GPIO_OTYPER_OT_7);

        // No pull-up/down
        GPIOB->PUPDR &= ~(GPIO_PUPDR_PUPDR0 | GPIO_PUPDR_PUPDR1 | GPIO_PUPDR_PUPDR2 | GPIO_PUPDR_PUPDR3 | GPIO_PUPDR_PUPDR4
                | GPIO_PUPDR_PUPDR5 | GPIO_PUPDR_PUPDR6 | GPIO_PUPDR_PUPDR7);
    }
}

void init_timer(void)
{
    // Enable clock for TIM14
    RCC->APB1ENR |= RCC_APB1ENR_TIM14EN;

    // TODO: Calculate PSC and ARR values correctly to simulate a 1s period.
    TIM14->PSC = 4999;  // Prescaler
    TIM14->ARR = 199; // Auto-reload register
    TIM14->CNT = 0;
    TIM14->DIER |= TIM_DIER_UIE; // Enable interrupts

    // Start the timer
    TIM14->CR1 |= TIM_CR1_CEN;
}

void write_leds(uint8_t pattern)
{
    // Clear all LEDs
    GPIOB->BRR = UINT8_MAX;
    GPIOB->BSRR = pattern;
}

void check_pb(void)
{
    // Read buttons
    int btn0 = (GPIOA->IDR & (1 << 0)) == FALSE;
    int btn1 = (GPIOA->IDR & (1 << 1)) == FALSE;
    int btn2 = (GPIOA->IDR & (1 << 2)) == FALSE;
    int btn3 = (GPIOA->IDR & (1 << 3)) == FALSE;

    // if (btn0)
    // {
    //     g_start_flag = TRUE;
    //     g_first_flag = FALSE;
    //     g_second_flag = FALSE;
    //     g_third_flag = FALSE;
    // }
    // else if (btn1)
    // {
    //     g_start_flag = FALSE;
    //     g_first_flag = TRUE;
    //     g_second_flag = FALSE;
    //     g_third_flag = FALSE;
    // }
    // else if (btn2)
    // {
    //     g_start_flag = FALSE;
    //     g_first_flag = FALSE;
    //     g_second_flag = TRUE;
    //     g_third_flag = FALSE;
    // }
    // else if (btn3)
    // {
    //     g_start_flag = FALSE;
    //     g_first_flag = FALSE;
    //     g_second_flag = FALSE;
    //     g_third_flag = TRUE;
    // }
}
