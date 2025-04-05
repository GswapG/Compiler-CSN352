#include <stdio.h>

int main() {
    int a = 10;
    int &ref = a;  // Reference variable
    // ref += 5;
    printf("a after modification via reference: %d\n", a);
    return 0;
}
