// #include <stdio.h>

void test_pointer_dereference() {
    int a = 10;           // Regular integer variable
    int *ptr = &a;        // Pointer to 'a'
    
    // printf("Before dereferencing: a = %d\n", a);

    // Dereferencing pointer to change the value of 'a'
    *ptr = 20;

    // printf("After dereferencing and modifying through ptr: a = %d\n", a);

    // Another dereferencing example: reading the value through the pointer
    int b = *ptr;
    int x = -1;
    // printf("Value read from pointer (b): %d\n", b);
}

int main() {
    test_pointer_dereference();
    // return 0;
}