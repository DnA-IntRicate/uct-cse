// Adam Foflonker
// 13/06/26

/**
 * Exercise 21
 *
 * Write a C program that does the following:
 * Each time SW0 is pushed:
 *  - Read the analogue voltage from a potentiometer connected to PA6 using the ADC.
 *  - Convert the ADC reading to a digital value in the range 0-63
 *
 * Use the digital value to control the LEDs such that:
 *  - ADC 0 - 7: No LEDs on
 *  - ADC 8 - 15: LED 1 on
 *  - ADC 16 - 23: LED 1, 2 on
 *  - ADC 24 - 31: LED 1, 2, 3 on
 *  - ...
 *  - ADC 56 - 63: LED 1 - 7 on
 */

#include <main.h>
#include "stm32f0xx.h"
#include <lcd_stm32f0.h>

#define TRUE 1
#define FALSE 0

// Initialize GPIO ports
void init_gpio(void);

// Initialize & start the ADC
void init_adc(void);

// Check push buttons
int check_pb(void);

// Read the ADC's value (8-bit only)
uint8_t read_adc(void);

// Set the state (on/off) of the LEDs on GPIOB
void write_leds(uint8_t pattern);

// Convert 8-bit unsigned integer to ASCII
void uitoa(uint8_t num, char *out_res);

int main(void)
{
    // Initialization
    init_gpio();
    init_adc();
    init_LCD();

    // Splash screen
    lcd_command(CLEAR);
    lcd_putstring("Ready");
    write_leds(1 << 7); // Turn D7 on

    while (TRUE)
    {
        if (check_pb())
        {
            uint8_t pot_value = read_adc();

            // Debug print the Pot's value
            char num_str[4] = {};
            uitoa(pot_value, num_str);
            lcd_command(CLEAR);
            lcd_putstring(num_str);

            if (pot_value <= 7) // 0-7: No LEDs on
                write_leds(0);
            else if ((pot_value >= 8) && (pot_value <= 15)) // 8-15: 1 LED
                write_leds(0b1);
            else if ((pot_value >= 16) && (pot_value <= 23)) // 16-23: 2 LEDs
                write_leds(0b11);
            else if ((pot_value >= 24) && (pot_value <= 31)) // 24-31: 3 LEDs
                write_leds(0b111);
            else if ((pot_value >= 32) && (pot_value <= 39)) // 32-39: 4 LEDs
                write_leds(0b1111);
            else if ((pot_value >= 40) && (pot_value <= 47)) // 40-47: 5 LEDs
                write_leds(0b11111);
            else if ((pot_value >= 48) && (pot_value <= 55)) // 48-55: 6 LEDs
                write_leds(0b111111);
            else if ((pot_value >= 56) && (pot_value <= 63)) // 56-63: 7 LEDs
                write_leds(0b1111111);
        }
    }
}

void init_gpio(void)
{
    // Enable Lights, push buttons and pots
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

    // Config SW0
    GPIOA->MODER &= ~(3 << 0); // Input
    GPIOA->PUPDR |= (1 << 0);  // Pull-down

    // Set PA6 (pot) to analogue
    GPIOA->MODER |= (3 << 12);

    // Config lights
    GPIOB->MODER &= ~((uint16_t)-1); // Output
    GPIOB->MODER |= (1 << 0) | (1 << 2) | (1 << 4) | (1 << 6) | (1 << 8) | (1 << 10) | (1 << 12) | (1 << 14);
}

void init_adc(void)
{
    // Enable ADC1 clock
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    // Single shot
    ADC1->CFGR1 &= ~ADC_CFGR1_CONT;

    // Right-align
    ADC1->CFGR1 &= ~ADC_CFGR1_ALIGN;

    // 6-bit mode (11)
    // Range: 0-63
    ADC1->CFGR1 |= ADC_CFGR1_RES;

    // Select channel 6 (only) as input (PA6)
    ADC1->CHSELR = ADC_CHSELR_CHSEL6;

    // Enable ADC
    ADC1->CR |= ADC_CR_ADEN;

    // Wait for ADC to be ready to begin conversion
    while ((ADC1->ISR & ADC_ISR_ADRDY) == 0)
        ;

    // Start ADC conversion
    ADC1->CR |= ADC_CR_ADSTART;
}

int check_pb(void)
{
    return (GPIOA->IDR & (1 << 0)) == 0;
}

uint8_t read_adc(void)
{
    // Wait for end of ADC conversion
    while ((ADC1->ISR & ADC_ISR_EOC) == 0)
        ;

    // Read ADC value
    volatile uint16_t res = ADC1->DR;

    // Convert again
    ADC1->CR = ADC_CR_ADSTART;

    return (uint8_t)res;
}

void write_leds(uint8_t pattern)
{
    // Clear and set LEDs
    GPIOB->BSRR = (((uint16_t)-1) << 16) | pattern;
}

void uitoa(uint8_t num, char *out_res)
{
    if (!out_res)
        return;

    out_res[0] = '0' + (num / 100);       // Hundreds
    out_res[1] = '0' + ((num / 10) % 10); // Tens
    out_res[2] = '0' + (num % 10);        // Units
    out_res[3] = '\0';                    // Null-termination char
}
