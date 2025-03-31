#include <stdio.h>
void test_integer_multiplication() {
    int a = 6, b = 3;
    printf("%d * %d = %d\n", a, b, a * b);
}

void test_integer_division() {
    int a = 7, b = 3;
    printf("%d / %d = %d\n", a, b, a / b);
}

void test_integer_modulo() {
    int a = 7, b = 3;
    printf("%d %% %d = %d\n", a, b, a % b);
}

void test_float_multiplication() {
    float a = 6.5, b = 2.0;
    printf("%f * %f = %f\n", a, b, a * b);
}

void test_float_division() {
    float a = 7.5, b = 2.5;
    printf("%f / %f = %f\n", a, b, a / b);
}

void test_usual_arithmetic_conversions() {
    int a = 5;
    float b = 2.5;
    printf("%d * %f = %f\n", a, b, a * b);
}

void test_division_by_zero() {
    int a = 5, b = 0;
    // Uncommenting the line below will cause undefined behavior
    // printf("%d / %d = %d\n", a, b, a / b);
    printf("Division by zero is undefined.\n");
}

void test_large_integer_division() {
    int a = 1, b = 2;
    printf("%d / %d = %d\n", a, b, a / b);
}

void test_integer_division_property() {
    int a = 10, b = 3;
    printf("Checking property: (%d / %d) * %d + (%d %% %d) == %d\n", a, b, b, a, b, a);
    int quotient = a / b;
    int remainder = a % b;
    printf("Result: %d\n", quotient * b + remainder);
}

int main() {
    test_integer_multiplication();
    test_integer_division();
    test_integer_modulo();
    test_float_multiplication();
    test_float_division();
    test_usual_arithmetic_conversions();
    test_division_by_zero();
    test_large_integer_division();
    test_integer_division_property();
    return 0;
}