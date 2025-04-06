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
            printf("%d%c\n", data.i, data.c);
            break;
    }
    return 0;
}
