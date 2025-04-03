#include <stdio.h>

struct Point {
    int x, y;
};

void printPoint(struct Point p) {
    printf("(%d, %d)\n", p.x, p.y);
}

int main() {
    printPoint((struct Point){ 1 });
    return 0;
}
