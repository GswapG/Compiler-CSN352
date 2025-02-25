#include <stdio.h>
#include <stdlib.h>

enum Status { SUCCESS, FAILURE };

union Data {
    int value;
    int *ptr;
};

int fibonacci(int n) {
    if(n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int n = 10;
    int **ppFib = (int **)malloc(sizeof(int *));
    if (!ppFib) return FAILURE;
    *ppFib = (int *)malloc(sizeof(int));
    if (!(*ppFib)) return FAILURE;
    
    union Data d;
    d.value = fibonacci(n);
    **ppFib = d.value;
    printf("Fibonacci(%d) = %d\n", n, **ppFib);
    
    free(*ppFib);
    free(ppFib);
    return SUCCESS;
}
