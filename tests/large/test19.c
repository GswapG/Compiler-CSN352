#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// typedef for a function pointer
typedef int (*Operation)(int, int);

// enum for operation types
enum OpType { ADD, SUBTRACT, MULTIPLY, DIVIDE };

// struct to hold operation details
struct OperationDetail {
    enum OpType type;
    Operation op;
};

// union for holding either an integer or a pointer
union Number {
    int val;
    int *ptr;
};

// Recursive function with a static counter
int recursive_compute(int n) {
    static int call_count = 0;
    call_count++;
    if(n <= 1) return 1;
    return n * recursive_compute(n - 1);
}

// Basic arithmetic operations
int add(int a, int b) { return a + b; }
int subtract(int a, int b){ return a - b; }
int multiply(int a, int b){ return a * b; }
int divide(int a, int b){ return (b != 0) ? a / b : 0; }

int main(int argc, char *argv[]) {
    // Command‑line input: expect factorial number and two numbers for arithmetic ops
    if(argc < 4) {
        printf("Usage: %s <fact_num> <op_a> <op_b>\n", argv[0]);
        return 1;
    }
    int fact_num = atoi(argv[1]);
    int op_a = atoi(argv[2]);
    int op_b = atoi(argv[3]);
    
    // Compute factorial recursively with dynamic memory allocation
    int *fact_result = (int *)malloc(sizeof(int));
    if(!fact_result) goto mem_error;
    *fact_result = recursive_compute(fact_num);
    printf("Factorial of %d is %d\n", fact_num, *fact_result);
    
    // Setup operations using struct and union
    struct OperationDetail ops[4];
    ops[0].type = ADD; ops[0].op = add;
    ops[1].type = SUBTRACT; ops[1].op = subtract;
    ops[2].type = MULTIPLY; ops[2].op = multiply;
    ops[3].type = DIVIDE; ops[3].op = divide;
    
    union Number number;
    number.val = op_a;
    
    // Multi‑dimensional array for operation inputs/results
    int results[4][2];
    for(int i = 0; i < 4; i++) {
        results[i][0] = number.val;
        results[i][1] = op_b;
    }
    
    // Nested loops with if‑else and switch cases to display operations
    for(int i = 0; i < 4; i++) {
        printf("Operation ");
        switch(ops[i].type) {
            case ADD: printf("Addition: "); break;
            case SUBTRACT: printf("Subtraction: "); break;
            case MULTIPLY: printf("Multiplication: "); break;
            case DIVIDE: printf("Division: "); break;
            default: printf("Unknown: "); break;
        }
        int res = ops[i].op(results[i][0], results[i][1]);
        printf("%d op %d = %d\n", results[i][0], results[i][1], res);
    }
    
    // File manipulation: write results to a file
    FILE *fp = fopen("final_output.txt", "w");
    if(!fp) goto file_error;
    fprintf(fp, "Factorial of %d is %d\n", fact_num, *fact_result);
    for(int i = 0; i < 4; i++)
        fprintf(fp, "Result %d: %d\n", i, ops[i].op(results[i][0], results[i][1]));
    fclose(fp);
    
    // Demonstrate do‑while with break/continue
    int dummy = 0;
    do {
        dummy++;
        if(dummy == 2) continue;
        if(dummy > 3) break;
        printf("Dummy in do‑while: %d\n", dummy);
    } while(dummy < 5);
    
    // Custom until loop: loop until dummy equals 5
    until(dummy == 5) {
        printf("Until loop dummy: %d\n", dummy);
        dummy++;
    }
    
    // Multi‑level pointer demonstration
    int value = 50;
    int *p = &value;
    int **pp = &p;
    printf("Multi‑level pointer value: %d\n", **pp);
    
    // C++‑style reference variable demonstration
    int x = 100;
    int &refX = x;
    refX += 50;
    printf("Reference variable x: %d\n", x);
    
    free(fact_result);
    return 0;
    
mem_error:
    printf("Memory allocation failed.\n");
    return 1;
file_error:
    printf("File operation failed.\n");
    return 1;
}
