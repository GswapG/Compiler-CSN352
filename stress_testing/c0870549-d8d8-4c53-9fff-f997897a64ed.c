#include <stdio.h>

int main() {
    // Arithmetic operators
    int a = 10, b = 3;

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


    // Conditional (ternary) operator
    int *p = &a;
    int max = (p) ? a : b;

    return 0;
}
