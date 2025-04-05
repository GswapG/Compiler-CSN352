#include <stdio.h>

int main() {
    int count = 0;
    do {
        printf("Count: %d\n", count);
        count++;
    } until(count == 5);
    return 0;
}
