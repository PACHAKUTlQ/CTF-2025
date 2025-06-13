#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// These are global constants used by the program
extern double DAT_00103138;  // First constant value
extern double DAT_00103140;  // Second constant value

// Generate random parameters for the expressions
int FUN_00101a77(double param1, double param2, double *result) {
    double random_val1, random_val2, random_val3;
    
    // Generate random values using rand() in the range [0,1]
    random_val1 = (double)rand() / RAND_MAX;
    random_val2 = (double)rand() / RAND_MAX;
    random_val3 = (double)rand() / RAND_MAX;
    
    // Scale random values using the input parameters
    result[0] = random_val1 * param1;
    result[1] = random_val2 * param2;
    result[2] = random_val3 * param1 * param2;
    
    return 1;
}

// Process the result values 
void FUN_00101b77(double *values) {
    // Some specific transformation applied to the evaluated expression results
    // This appears to be normalizing or adjusting the values for comparison
    values[0] = values[0] / 10.0;
    values[1] = values[1] * 2.0;
    values[2] = sqrt(values[2]);
}

// Check if the parameters and values match a specific relationship
// This is the key function that determines if the expressions are correct
int check1(double *params, double *values) {
    double epsilon = 0.0001;  // Small tolerance for floating-point comparison
    double expected1, expected2, expected3;
    
    // Calculate expected values based on parameters
    expected1 = params[0] + params[1];       // a + b
    expected2 = params[0] * params[1] * 2.0; // 2 * a * b
    expected3 = params[2] * params[2];       // c^2
    
    // Check if the evaluated values match the expected values within tolerance
    if (fabs(values[0] - expected1) > epsilon) return 0;
    if (fabs(values[1] - expected2) > epsilon) return 0;
    if (fabs(values[2] - expected3) > epsilon) return 0;
    
    return 1;  // All checks passed
}

// Constants used by the program
double DAT_00103138 = 100.0;  // Placeholder value - may need to be adjusted
double DAT_00103140 = 200.0;  // Placeholder value - may need to be adjusted
