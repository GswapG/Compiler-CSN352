#include <stdio.h>

int main() {
    int option = 2;
    switch(option) {
        case 1:
            printf("Option 1 selected.\n");
            break;
        case 2:
            printf("Option 2 selected.\n");
            break;
        default:
            printf("Unknown option.\n");
    }
    return 0;
}
