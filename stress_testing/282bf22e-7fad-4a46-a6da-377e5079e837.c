
int i = 128;
long l = 128;

int int_to_pointer(void) {
    int *a = (int *) i;
    int *b = (int *) l;
    return a == b;
}

int pointer_to_int(void) {
    static long l;
    long *ptr = &l;
    unsigned long ptr_as_long = (unsigned long) ptr;
    /* This will be divisible by eight, since long is eight byte-aligned */
    return (ptr_as_long % 8 == 0);
}

int cast_long_round_trip(void) {
    int *ptr = (int *) l;
    long l2 = (long) ptr;
    return (l == l2);
}

int cast_ulong_round_trip(void) {
    long *ptr = &l;
    unsigned long ptr_as_ulong = (unsigned long) ptr;
    long *ptr2 = (long *) ptr_as_ulong;
    return (ptr == ptr2);
}

// int to pointer and back
int cast_int_round_trip(void) {
    double *a = (double *)i;
    int i2 = (int) a;
    return (i2 == 128);
}
int main(void) {
    if (!int_to_pointer()) {
        return 1;
    }
    if (!pointer_to_int()) {
        return 2;
    }
    if (!cast_long_round_trip()) {
        return 3;
    }
    if (!cast_ulong_round_trip()) {
        return 4;
    }
    if (!cast_int_round_trip()) {
        return 5;
    }
    return 0;
}