#include <stdio.h>

struct Point {
    int x;
};

int main() {
    int x = 10;
    int arr[5] = {1, 2, 3};
    *(arr + 5) = x;

    int *ptr = &arr[0];
    arr[0] = *ptr;

    arr[1] = arr[2];
}
