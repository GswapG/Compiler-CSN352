#include <stdio.h>

int main() {
    int arr[5][2] = {{10,1}, {20,2}, {30,3}, {40,4}, {50,5}};
    int i = 10;
    for (int i = 0; i < 5; i++) {
        i = 1;
        for(int j = 0; j<5; j++){
            printf("arr[%d][%d] = %d\n", i, j, arr[i][j]);
        }
        
    }
    return 0;
}
