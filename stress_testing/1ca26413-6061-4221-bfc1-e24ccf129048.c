#include <stdio.h>

struct Point {
    int x;
};

int main() {
    int x = 10;
    x += (x = 5);
}
