#include <stdio.h>

int main() {
    int arr[5][2] = {{10,1}, {20,2}, {30,3}, {40,4}, {50,5}};
    arr[1][7] = arr[1][4];
    return 0;
}