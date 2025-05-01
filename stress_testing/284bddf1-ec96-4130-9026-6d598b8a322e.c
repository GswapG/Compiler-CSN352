#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int a[10][10];
    for(int i = 0;i<10;i++){
        for(int j = 0;j<10;j++){
            a[i][j] = 0;
        }
    }
    for(int i = 0;i<10;i++){
        a[i][i] = 1;
    }
}