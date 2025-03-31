#include <stdio.h>
// #include <limits.h>

int main() {
    int a = 10, b = 3;
    float x = 5.5, y = 2.0;
    
    // Integer multiplication, division, and modulus
    printf("%d * %d = %d\n", a, b, a * b);
    printf("%d / %d = %d\n", a, b, a / b);
    printf("%d %% %d = %d\n", a, b, a % b);

    // Floating-point multiplication and division
    printf("%f * %f = %f\n", x, y, x * y);
    printf("%f / %f = %f\n", x, y, x / y);

    // Usual arithmetic conversion (int and float)
    printf("%d * %f = %f\n", a, y, a * y);
    printf("%d / %f = %f\n", a, y, a / y);

    // Large integer operations
    printf("%d * 2 = %d\n", 10, 10 * 2);
    
    return 0;
}
