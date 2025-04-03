#include <stdio.h>
int main() {
    int i = 1;
loop:
    if (i > 5) return 0;
    printf("%d\n", i);
    i++;
    goto loop;
}
