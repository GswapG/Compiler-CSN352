/* Pure C Code Stress Test (No Preprocessor Processing) */

/* Structures, Unions, and Enumerations */
struct S1 {
    int a;
    double b;
};

union U1 {
    struct S1 s;
    long l;
};

enum MyEnum {
    VAL1 = 1,
    VAL2 = 2,
    VAL3 = 3
};

/* Typedef for function pointer */
typedef int (*func_ptr)(int, int);

/* Basic arithmetic functions */
int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

/* Functions simulating multiple code constructs */
void one_func(void) {
    /* Function body for one_func */
}

void two_func(void) {
    /* Function body for two_func */
}

void three_func(void) {
    /* Function body for three_func */
}

/* Functions with simple names */
int myfunc1(int x) {
    return x;
}

int test_func(int x) {
    return x * 2;
}

/* Function demonstrating variable-length arrays (VLAs) */
void vla_example(int n) {
    int arr[n];
    int i;
    for (i = 0; i < n; i++) {
        arr[i] = i * i;
    }
    for (i = 0; i < n; i++) {
        /* Process each element (e.g., for debugging or analysis) */
    }
}

/* Function demonstrating pointer casts and void* usage */
void pointer_tricks(void) {
    int x = 10;
    int *p = &x;
    void *vp = (void *)p;
    int *p2 = (int *)vp;
}

/* Structure with bit-fields */
struct BitField {
    unsigned int a : 3;
    unsigned int b : 5;
};

/* Tail-recursive function */
int tail_recursion(int n, int acc) {
    if (n == 0)
        return acc;
    return tail_recursion(n - 1, acc + n);
}

/* Switch-case construct with intentional fallthrough */
void switch_example(int n) {
    switch (n) {
        case 1:
            /* fallthrough intended */
        case 2:
            break;
        default:
            break;
    }
}

/* Inline function (using C99 semantics) */
static inline int inline_function(int a, int b) {
    return a - b;
}

/* Inline assembly example (GCC-style inline assembly) */
void asm_example(void) {
    __asm__("nop");
}

/* Main function exercising all constructs */
int main(void) {
    int a = 5, b = 10;
    int result;
    int i;

    result = add(a, b);
    result = multiply(a, b);
    result = myfunc1(42);
    result = test_func(21);

    vla_example(5);
    pointer_tricks();

    /* Bit-field variable test */
    struct BitField bf;
    bf.a = 5;
    bf.b = 17;

    result = tail_recursion(10, 0);
    switch_example(1);
    switch_example(3);
    result = inline_function(20, 10);

    /* Array of function pointers */
    // func_ptr functions[2];
    // functions[0] = add;
    // functions[1] = multiply;
    // for (i = 0; i < 2; i++) {
    //     result = functions[i](a, b);
    // }

    while (1 == 1) {
        for (int i = 1, j = 1; i <= 100 && j <= 1000; i++) {
            printf("what the fuck is this %d\n%d", i, j);
        }
    }   

    asm_example();

    one_func();
    two_func();
    three_func();

    return 0;
}