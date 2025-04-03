#include <stdio.h>

enum Color { RED, GREEN, BLUE };

int main() {
    enum Color favorite = GREEN;
    if(favorite == GREEN)
        printf("Favorite color is green.\n");
    else
        printf("Favorite color is not green.\n");
    return 0;
}