#include <stdio.h>

int main() {
    int arr[5][2] = {{10,1}, {20,2}, {30,3}, {40,4}, {50,5}};
    const unsigned int ar[5][2] = {{10,1}, {20,2}, {30,3}, {40,4}, {50,5}};
    arr[1] = arr[3];
    // int x = 5;
    // int arr = 10;
    return 0;
}