#include <stdio.h>

struct Point {
    int x, y;
};

void printPoint(struct Point p) {
    printf("(%d, %d)\n", p.x, p.y);
}

int main() {
    printPoint((struct Point){ 10, 20 });  // Creates a temporary struct
    return 0;
}
