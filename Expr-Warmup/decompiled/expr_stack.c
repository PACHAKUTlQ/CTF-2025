#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// Expression evaluation functions

// Initialize the expression with parameters a, b, c
void init_expr(double a, double b, double c, void *expr) {
    int *stack_ptr = (int *)((char *)expr + 800);
    double **params = (double **)((char *)expr + 0x328);
    
    *stack_ptr = -1;  // Initialize stack pointer
    params[0] = &a;   // Store parameter a
    params[1] = &b;   // Store parameter b
    params[2] = &c;   // Store parameter c
}

// Push a value onto the stack
void push(double value, void *stack) {
    int *stack_ptr = (int *)((char *)stack + 800);
    double *stack_values = (double *)stack;
    
    if (*stack_ptr >= 98) {  // Stack overflow check (0x62)
        fwrite("Stack overflow\n", 1, 15, stderr);
        exit(1);
    }
    
    (*stack_ptr)++;
    stack_values[*stack_ptr] = value;
}

// Pop a value from the stack
double pop(void *stack) {
    int *stack_ptr = (int *)((char *)stack + 800);
    double *stack_values = (double *)stack;
    
    if (*stack_ptr < 0) {  // Stack underflow check
        fwrite("Stack underflow\n", 1, 16, stderr);
        exit(1);
    }
    
    double value = stack_values[*stack_ptr];
    (*stack_ptr)--;
    return value;
}

// Process a token in the expression
void process_token(void *expr, char *token) {
    double a, b, result;
    
    switch(token[0]) {
        case 'a':  // Push parameter a
            push(*(double *)(*(long *)((char *)expr + 0x328)), expr);
            break;
            
        case 'b':  // Push parameter b
            push(*(double *)(*(long *)((char *)expr + 0x330)), expr);
            break;
            
        case 'c':  // Push parameter c
            push(*(double *)(*(long *)((char *)expr + 0x338)), expr);
            break;
            
        case 'p':  // Addition
            b = pop(expr);
            a = pop(expr);
            push(a + b, expr);
            break;
            
        case 'm':  // Subtraction
            b = pop(expr);
            a = pop(expr);
            push(a - b, expr);
            break;
            
        case 'x':  // Multiplication
            b = pop(expr);
            a = pop(expr);
            push(a * b, expr);
            break;
            
        case 'd':  // Division
            b = pop(expr);
            a = pop(expr);
            push(a / b, expr);
            break;
            
        case 's':  // Square
            a = pop(expr);
            push(a * a, expr);
            break;
            
        case 'r':  // Square root
            a = pop(expr);
            push(sqrt(a), expr);
            break;
            
        default:  // Try to parse as a number
            char *end_ptr;
            double value = strtod(token, &end_ptr);
            if (token == end_ptr) {
                fwrite("Error: Invalid token\n", 1, 21, stderr);
                exit(1);
            }
            push(value, expr);
            break;
    }
}

// Evaluate an expression with given tokens
double evaluate(void *expr, char **tokens, int count) {
    int i;
    
    for (i = 0; i < count; i++) {
        process_token(expr, tokens[i]);
    }
    
    // Check for errors
    int *stack_ptr = (int *)((char *)expr + 800);
    if (*stack_ptr != 0) {
        fwrite("Error: Invalid expression\n", 1, 26, stderr);
        exit(1);
    }
    
    return pop(expr);
}

// Split a string by delimiter into tokens
void* split(char *str, char delimiter, int *count) {
    size_t len = strlen(str);
    int token_count = 1;
    int i, start_idx, token_len;
    char **tokens, *token;
    
    // Count the number of tokens
    for (i = 0; i < len; i++) {
        if (str[i] == delimiter) {
            token_count++;
        }
    }
    
    // Allocate memory for tokens array
    tokens = (char **)malloc(token_count * sizeof(char *));
    if (tokens == NULL) {
        return NULL;
    }
    
    // Split the string
    start_idx = 0;
    token_count = 0;
    
    for (i = 0; i <= len; i++) {
        if (str[i] == delimiter || str[i] == '\0') {
            token_len = i - start_idx;
            token = (char *)malloc(token_len + 1);
            
            if (token == NULL) {
                // Free already allocated tokens
                for (int j = 0; j < token_count; j++) {
                    free(tokens[j]);
                }
                free(tokens);
                return NULL;
            }
            
            strncpy(token, str + start_idx, token_len);
            token[token_len] = '\0';
            
            tokens[token_count] = token;
            token_count++;
            
            start_idx = i + 1;
        }
    }
    
    *count = token_count;
    return tokens;
}

// Free allocated tokens
void free_tokens(char **tokens, int count) {
    int i;
    
    for (i = 0; i < count; i++) {
        free(tokens[i]);
    }
    free(tokens);
}
