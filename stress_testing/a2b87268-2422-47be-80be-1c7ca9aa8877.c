#include <stdio.h>

struct Point {
    int x;
};

int main() {
    int arr[2] = {2, 3};
    struct Point p = {arr[0]};
    int a = 10;
    float b = 10.5;
    int *q = &a;
    int max = (q) ? a : b;
}
