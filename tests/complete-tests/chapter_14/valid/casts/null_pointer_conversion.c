/* Make sure we can implicity convert null pointer constants to pointer type */

// convert static variable initializers
double *d;
int *i;
int *i2;

int main(void)
{
    int x = 10;
    int *ptr = &x;

    // check static initializers
    if (d) {
        return 1;
    }

    if (i) {
        return 2;
    }
    if (i2) {
        return 3;
    }

    // convert to pointer for assignment
    if (ptr) {
        return 4;
    }

    // convert pointer in non-static initializer
    int *y;
    if (y)
        return 5;

    // convert function argument to pointer
    // if (!expect_null_param(0)) {
    //     return 6;
    // }

    // return_null_ptr converts a null pointer constant to a pointer
    long *null_ptr;
    if (null_ptr) {
        return 7;
    }

    // convert ternary operand to null pointer
    ptr = &x; // now pointer is non-null
    int *ternary_result;
    if (ternary_result) {
        return 8;
    }

    return 0;
}