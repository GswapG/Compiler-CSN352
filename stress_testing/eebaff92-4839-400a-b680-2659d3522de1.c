#include <stdio.h>

unsigned long factorial(unsigned long n) {
    if(n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    unsigned long num = 5;
    printf("Factorial of %d is %d\n", num, factorial(num));
    return 0;
}
