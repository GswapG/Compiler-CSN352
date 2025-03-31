#include <stdio.h>

struct Point {
    int x;
};

int main() {
    int arr[2] = {2, 3};
    struct Point p = {arr[0]};
    int* q = (int*)&p;
}
