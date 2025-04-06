#include <stdio.h>

union Data {
    int i;
    char c;
};

int main() {
    union Data data;
    int xx=3;
    data.i = 65;
    
    switch(data.i) {
        case 65:
            printf("%d%c\n", data.i, data.c);
            break;
        default:
            xx=2;
    }
    return 0;
}
