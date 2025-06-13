#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <math.h>

// Function declarations
void* split(char *str, char delimiter, int *count);
void init_expr(double a, double b, double c, void *expr);
void push(double value, void *stack);
double pop(void *stack);
void process_token(void *expr, char *token);
double evaluate(void *expr, char **tokens, int count);
int FUN_00101a77(double param_1, double param_2, double *result);
void FUN_00101b77(double *values);
int check1(double *params, double *values);
void free_tokens(char **tokens, int count);

// Main function declaration
int main(void);

// Main function implementation
int main(void) {
    uint32_t rand_seed;
    int fd, read_result;
    char *input1 = NULL, *input2 = NULL, *input3 = NULL;
    size_t len = 0;
    char **tokens1, **tokens2, **tokens3;
    int token_count1, token_count2, token_count3;
    double params[3], values[3];
    char *flag;
    void *expr_buffer[210]; // 840 bytes for expression stack
    int i;
    
    // Initialize random seed from /dev/urandom
    fd = open("/dev/urandom", O_RDONLY);
    read_result = read(fd, &rand_seed, 4);
    
    if (read_result != 4) {
        return -1;
    }
    
    close(fd);
    srand(rand_seed);
    
    // Get three input expressions from user
    printf("> ");
    getline(&input1, &len, stdin);
    printf("> ");
    getline(&input2, &len, stdin);
    printf("> ");
    getline(&input3, &len, stdin);
    
    // Remove trailing newlines
    input1[strcspn(input1, "\n")] = '\0';
    input2[strcspn(input2, "\n")] = '\0';
    input3[strcspn(input3, "\n")] = '\0';
    
    // Split inputs by spaces into tokens
    tokens1 = split(input1, ' ', &token_count1);
    tokens2 = split(input2, ' ', &token_count2);
    tokens3 = split(input3, ' ', &token_count3);
    
    free(input1);
    free(input2);
    free(input3);
    
    // Try 10 times to find correct parameters
    for (i = 0; i < 10; i++) {
        // Generate random parameters
        FUN_00101a77(DAT_00103140, DAT_00103138, params);
        
        // Evaluate expressions with the generated parameters
        init_expr(params[0], params[1], params[2], expr_buffer);
        values[0] = evaluate(expr_buffer, tokens1, token_count1);
        
        init_expr(params[0], params[1], params[2], expr_buffer);
        values[1] = evaluate(expr_buffer, tokens2, token_count2);
        
        init_expr(params[0], params[1], params[2], expr_buffer);
        values[2] = evaluate(expr_buffer, tokens3, token_count3);
        
        // Process the values
        FUN_00101b77(values);
        
        // Check if the expressions with these parameters match expected values
        if (check1(params, values) == 0) {
            puts("Never gives up!");
            free_tokens(tokens1, token_count1);
            free_tokens(tokens2, token_count2);
            free_tokens(tokens3, token_count3);
            return 0;
        }
    }
    
    // Success! Output the flag
    flag = getenv("FLAG");
    if (flag == NULL) {
        puts("Flag missing, contact an admin");
    } else {
        puts(flag);
    }
    
    // Clean up
    free_tokens(tokens1, token_count1);
    free_tokens(tokens2, token_count2);
    free_tokens(tokens3, token_count3);
    
    return 0;
}
