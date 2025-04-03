#include <stdio.h>

union Data {
    int i;
    float f;
};

int main() {
    union Data d;
    d.i = 100;
    int x = 10;
    printf("Unioninteger:%d\n", x);
    d.f = 3.14;
    printf("Unionasfloat:%f\n", d.f);
    return 0;
}