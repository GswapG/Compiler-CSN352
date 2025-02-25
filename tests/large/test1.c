#include <stdio.h>
#include <stdlib.h>

typedef unsigned long ulong;

ulong factorial(ulong n) {
    if(n <= 1) return 1;
    return n * factorial(n - 1);
}

int main(int argc, char *argv[]) {
    if(argc < 2) {
        printf("Usage: %s <number>\n", argv[0]);
        return 1;
    }
    ulong n = strtoul(argv[1], NULL, 10);
    ulong *result = (ulong *)malloc(sizeof(ulong));
    if (!result) {
        printf("Memory allocation failed\n");
        return 1;
    }
    *result = factorial(n);
    printf("Factorial of %lu is %lu\n", n, *result);
    free(result);
    return 0;
}
