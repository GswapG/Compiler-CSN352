#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(5, 7);
    int a = 2;
    if(a < 2){
        printf("Hello");
    }
    printf("5 + 7 = %d\n", result);
    return 0;
}
