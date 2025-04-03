int main() {
    int a = 1;
    int b = 2;
    int eq  = (1 == 2);       // equality
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
    // int max = (a > b) ? a : b;
}