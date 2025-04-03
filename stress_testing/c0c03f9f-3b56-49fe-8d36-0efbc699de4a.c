
#include <stdio.h>
int main() {
    {
        goto inside;
    inside:
        printf("Block label reached\n");
    }
    return 0;
}
