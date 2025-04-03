#include <stdio.h>

struct Point {
    int x;
};

int main() {
    int x = 10;
    int arr[5] = {1, 2, 3};
    *(arr + 5) = x;

    int *ptr = &x;
}
