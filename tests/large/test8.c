#include <stdio.h>
#include <stdlib.h>

enum Color { RED, GREEN, BLUE };

union Value {
    int i;
    double d;
};

int main() {
    int a = 10;
    // C++‑style reference variable
    int &ref = a;
    ref = 20;
    printf("a: %d, ref: %d\n", a, ref);
    
    // Dynamic allocation for union
    union Value *val = (union Value*)malloc(sizeof(union Value));
    if(!val) {
        printf("Allocation failed\n");
        return 1;
    }
    val->i = 42;
    printf("Union value as int: %d\n", val->i);
    free(val);
    
    // Using enum
    enum Color favorite = BLUE;
    if(favorite == BLUE)
        printf("Favorite color is blue.\n");
    else
        printf("Favorite color is not blue.\n");
    
    return 0;
}
