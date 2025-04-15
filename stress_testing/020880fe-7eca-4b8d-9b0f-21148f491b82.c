#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int hi;
    goto label;
    label:
    printf("hello");
}
