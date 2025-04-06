#include <stdio.h>
#include <stdlib.h>

int main() {
    int arr[10];
    // Initialize array with a complex arithmetic expression
    for (int i = 0; i < 10; i++) {
        arr[i] = i * i - i + 3 * (i + 2) - 5;
    }
    
    // Complex expression to test associativity rules
    int a = 5, b = 3, c = 2, d = 8;
    int result = a + b * c - d / (a - b) + (c % d);
    printf("Result of complex arithmetic: %d\n", result);
    
    // Nested loops with break and continue
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            if(i == j) continue;
            if(i + j > 15) break;
            printf("Pair (%d, %d)\n", i, j);
        }
    }
    
    // Demonstrate pointer arithmetic
    int *ptr = arr;
    for (int i = 0; i < 10; i++) {
        printf("arr[%d] = %d (via pointer: %d)\n", i, arr[i], *(ptr + i));
    }
    
    return 0;
}
