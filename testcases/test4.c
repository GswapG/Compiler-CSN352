extern int extVar;
_Static_assert(sizeof(int) >= 2, "int too small");

inline int add(int a, int b) {
    return a + b;
}

static int sub(int a, int b) {
    return a - b;
}

/* Structure definition using _Alignas */
struct Node {
    int data;
    struct Node *next;  /* PTR_OP usage */
};

/* Union definition */
union Data {
    int i;
    float f;
};

/* Typedef for union */
typedef union Data DataType;

/* Enumeration definition */
enum Color { RED, GREEN, BLUE };

int color_code(enum Color col) {
    switch(col) {
        case RED:
            return 1;
        case GREEN:
            return 2;
        case BLUE:
            return 3;
        default:
            return 0;
    }
}

/* Function with variable arguments (ellipsis punctuator) */
int varfunc(int count, ...) {
    return count;
}

int main(void) {
    /* Variable declarations using reserved keywords */
    auto int autoVar = 1;
    register int regVar = 2;
    volatile int volVar = 3;
    const int constVar = 4;
    static int staticVar = 5;
    long longVar = 6;
    signed int sInt = -7;
    unsigned int uInt = 8;
    short shortVar = 9;

    /* Other tokens: I_CONSTANT, F_CONSTANT, CHAR_CONSTANT, STRING_LITERAL */
    int a = 10, b = 3;
    float f = 3.14;
    double d = 2.71828;
    char ch = 'A';
    char str[] = "Test String";

    /* _Bool, _Complex, _Imaginary, _Atomic, _Thread_local */
    _Bool flag = 1;
    _Complex float comp = 1.0 + 2.0 * 1.0;
    _Atomic int atomic_var = 0;

    /* _Generic usage */
    const char* type_str = _Generic(a, int: "int", default: "other");

    /* _Alignof and typedef (using unsigned and long) */
    typedef unsigned long my_size_t;

    /* Arithmetic operators */
    int sum = a + b;
    int diff = a - b;
    int prod = a * b;
    int quot = a / b;
    int rem = a % b;
    a++;
    b--;

    /* Relational operators */
    if(a == b) { }
    if(a != b) { }
    if(a > b) { }
    if(a < b) { }
    if(a >= b) { }
    if(a <= b) { }

    /* if-else statement */
    if(a < b) {
        a = b;
    } else {
        a = a;
    }

    /* Bitwise operators */
    int bw_and = a & b;
    int bw_or = a | b;
    int bw_xor = a ^ b;
    int bw_tilde = ~a;
    int bw_left = a << 2;
    int bw_right = a >> 2;

    /* Logical operators */
    if(a && b) { }
    if(a || b) { }
    if(!a) { }

    /* Assignment operators */
    a = 5;
    a += 2;
    a -= 1;
    a *= 3;
    a /= 2;
    a %= 2;
    a <<= 1;
    a >>= 1;
    a &= 3;
    a ^= 2;
    a |= 1;

    /* Ternary operator */
    int c = (a > b) ? a : b;

    /* Loop constructs: for, while, and do-until (using reserved "until") */
    int i;
    for(i = 0; i < 5; i++) {
        if(i == 2)
            continue;
        if(i == 4)
            break;
    }
    
    int j = 0;
    while(j < 5) {
        j++;
    }
    
    int k = 5;
    do {
        k--;
    } until(k == 0);

    /* Switch-case with enumeration constants */
    enum Color color = RED;
    int code = color_code(color);
    if(code == 0) {
        goto error;
    }

    /* Structure and pointer usage (PTR_OP) */
    struct Node node;
    struct Node *pnode = &node;
    pnode->data = 100;

    /* Using restrict with a pointer */
    int * restrict ptr = &a;

    /* Function calls using FUNC_NAME tokens */
    int result1 = add(a, b);
    int result2 = sub(a, b);
    int var_res = varfunc(3, a, b, c);

    return 0;
error:
    return 1
}