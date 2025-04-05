#include <stdio.h>

union Data {
    int i;
    char c;
};

int main() {
    union Data data;
    data.i = 65;
    
    switch(data.i) {
        case 65:
            printf("Value is 65, as int: %d and as char: %c\n", data.i, data.c);
            break;
        default:
            printf("Other value\n");
    }
    return 0;
}
