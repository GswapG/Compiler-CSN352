#include <stdio.h>

struct Data {
    float a;
    int b;
};

int main() {
    struct Data d = {3.14, 42};
    d.a -= 5.5;
    
}
