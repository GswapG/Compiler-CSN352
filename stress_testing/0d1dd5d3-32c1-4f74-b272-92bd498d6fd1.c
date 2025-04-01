#include <stdio.h>
int main() {
    goto label;
label:
    printf("Reached label!\n");
    return 0;
}
