#include <stdio.h>

int main() {
    for (int i = 0; i < 5; i++) {
        if(i % 2 == 0)
            printf("%d is even\n", i);
        if(2 % 2 == 0)
            printf("%d",i);
    }
}
