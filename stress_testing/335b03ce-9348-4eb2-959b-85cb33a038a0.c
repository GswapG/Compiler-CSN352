#include <stdio.h>

int main() {
    // Arithmetic operators
    int a = 10, b = 3;
    int sum = a + b;          // addition
    int diff = a - b;         // subtraction
    int prod = a * b;         // multiplication
    int quot = a / b;         // division
    int rem = a % b;          // modulus

    // Bitwise operators
    int bit_and = a & b;      // bitwise AND
    int bit_or  = a | b;       // bitwise OR
    int bit_xor = a ^ b;       // bitwise XOR
    int bit_not = ~a;         // bitwise NOT
    int shift_left = a << 1;  // left shift
    int shift_right = a >> 1; // right shift

    // Relational operators (result is either 0 (false) or 1 (true))
    int eq  = (a == b);       // equality
    int ne  = (a != b);       // not equal
    int lt  = (a < b);        // less than
    int gt  = (a > b);        // greater than
    int le  = (a <= b);       // less than or equal to
    int ge  = (a >= b);       // greater than or equal to

    // Logical operators
    int logical_and = (a > 5) && (b < 5);
    int logical_or  = (a < 5) || (b < 5);
    int logical_not = !(a < b);

    // Assignment operators
    int assign = 5;
    assign += 3;              // add and assign
    assign -= 2;              // subtract and assign
    assign *= 2;              // multiply and assign
    assign /= 3;              // divide and assign
    assign %= 2;              // modulus and assign

    // Conditional (ternary) operator
    int max = (a > b) ? a : b;

    // Print results
    printf("Arithmetic:\n");
    printf("a + b = %d\n", sum);
    printf("a - b = %d\n", diff);
    printf("a * b = %d\n", prod);
    printf("a / b = %d\n", quot);
    printf("a %% b = %d\n\n", rem);

    printf("Bitwise:\n");
    printf("a & b = %d\n", bit_and);
    printf("a | b = %d\n", bit_or);
    printf("a ^ b = %d\n", bit_xor);
    printf("~a = %d\n", bit_not);
    printf("a << 1 = %d\n", shift_left);
    printf("a >> 1 = %d\n\n", shift_right);

    printf("Relational:\n");
    printf("a == b: %d\n", eq);
    printf("a != b: %d\n", ne);
    printf("a < b:  %d\n", lt);
    printf("a > b:  %d\n", gt);
    printf("a <= b: %d\n", le);
    printf("a >= b: %d\n\n", ge);

    printf("Logical:\n");
    printf("(a > 5) && (b < 5): %d\n", logical_and);
    printf("(a < 5) || (b < 5): %d\n", logical_or);
    printf("!(a < b): %d\n\n", logical_not);

    printf("Assignment (final assign value): %d\n\n", assign);
    printf("Ternary: max(a, b) = %d\n", max);

    return 0;
}
