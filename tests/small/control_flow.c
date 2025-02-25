#include <stdio.h>

int main() {
    for (int i = 0; i < 5; i++) {
        if(i % 2 == 0)
            printf("%d is even\n", i);
        else
            printf("%d is odd\n", i);
    }
    int i = 0;
    while(i < 5) {
        printf("i: %d\n", i);
        i++;
    }
    i = 0;
    do {
        printf("i in do-while: %d\n", i);
        i++;
    } while(i < 5);
    
    return 0;
}
