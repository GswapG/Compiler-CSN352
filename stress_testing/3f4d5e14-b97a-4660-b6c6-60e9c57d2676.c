#include <stdio.h>

int func(int x){
    return 1;
}
int main() {
    int i,j,arr[2][3];
    func(arr);
    printf("%d",arr);
}
