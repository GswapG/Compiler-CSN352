#include <stdio.h>

int add(int a,int) {
    return a + 3;
}

int multiply(int a,int b) {
    return a * 3;
}

void operate(int x, int (*func)(int,int)) {
    int y = func(7);
}

int main() {
    operate(5, add);      // Output: 8
    operate(5, multiply); // Output: 15
    return 0;
}
