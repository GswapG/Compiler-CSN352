#include <stdio.h>

int add(int a) {
    return a + 3;
}

int multiply(int a) {
    return a * 3;
}

void operate(int x, int (*func)(int)) {
    int x = func(7);
}

int main() {
    int x = add(2);    // Output: 8
    // operate(5, multiply); // Output: 15
    return 0;
}
