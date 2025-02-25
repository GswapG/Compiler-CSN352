#include <stdio.h>

union Data {
    int i;
    float f;
};

int main() {
    union Data d;
    d.i = 100;
    printf("Union as integer: %d\n", d.i);
    d.f = 3.14f;
    printf("Union as float: %f\n", d.f);
    return 0;
}
