#include <stdio.h>

int main() {
    float x = 5.5;
    float *ptr = &x;

    // Invalid: Multiplication between a pointer and a float
    // float result1 = ptr * x; //   ERROR: Cannot multiply a pointer by float

    // Invalid: Division between a pointer and a float
    // float result2 = ptr / x; //   ERROR: Pointer cannot be divided

    return 0;
}
