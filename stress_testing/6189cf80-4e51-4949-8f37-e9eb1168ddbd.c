#include <stdio.h>
#include <stdlib.h>

int main() {
    void * z = malloc(2);
    int *p = (int *)z;
    if(!p) {
        printf("Memory allocation failed.\n");
        return 1;
    }
    *p = 42;
    printf("Allocated integer: %d\n", *p);
    free(p);
    return 0;
}
