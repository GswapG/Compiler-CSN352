#include <stdio.h>
#include <stdlib.h>

// Struct Definitions
struct A { int x; };
struct B { int y; };

void test_valid_casts() {
    // Scalar Casts
    int i = 42;
    float f = (float)i;  // int -> float (Valid)
    double d = (double)f;  // float -> double (Valid)
    char c = (char)i;  // int -> char (Valid)
    
    // Pointer Casts
    int *pi = &i;
    // void *vp = (void*)pi;  // int* -> void* (Valid)
    // pi = (int*)vp;  // void* -> int* (Valid)
    
    // Struct Pointer Casts
    struct A a;
    struct A *pa = &a;
    // void *vpa = (void*)pa;  // struct* -> void* (Valid)
    // pa = (struct A*)vpa;  // void* -> struct* (Valid)
    
    printf("Valid casts executed successfully.\n");
}

void test_invalid_casts() {
    struct A a;
    struct B b;
    
    // Struct to Struct Cast (Invalid)
    // b = (struct B)a;  //   ERROR: Structs are incompatible
    
    // Struct to Arithmetic Type Cast (Invalid)
    // int num = (int)a;  //   ERROR: Struct to int not allowed
    
    // Arithmetic Type to Struct Cast (Invalid)
    // a = (struct A)42;  //   ERROR: Cannot cast int to struct
    
    // Function Pointer to Data Pointer Cast (Implementation-Defined, Typically Invalid)
    // void (*func_ptr)() = test_valid_casts;
    // int *invalid_ptr = (int*)func_ptr;  //   ERROR: Function pointer to data pointer
    
    printf("Invalid cast cases commented out to prevent compiler errors.\n");
}

void test_pointer_casts() {
    int i = 10;
    int *ip = &i;
    char *cp = (char*)ip;  // Data pointer cast (Valid but risky)
    
    struct A a;
    struct A *ap = &a;
    struct B *bp;
    // bp = (struct B*)ap;  //   ERROR: Struct A* to Struct B* (Strictly Invalid)
    
    printf("Pointer casting tested. Some cases commented out due to errors.\n");
}

int main() {
    test_valid_casts();
    test_invalid_casts();
    test_pointer_casts();
    return 0;
}
