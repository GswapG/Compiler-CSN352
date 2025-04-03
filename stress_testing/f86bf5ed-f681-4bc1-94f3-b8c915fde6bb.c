#include <stdio.h>
int main() {
    goto first;
second:
    printf("Second Label\n");
    return 0;
first:
    printf("First Label\n");
    goto second;
}
