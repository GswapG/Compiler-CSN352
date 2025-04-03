#include <stdio.h>

void counter() {
    static int count = 0;
    count++;
    printf("Functioncount:%d\n", count);
}