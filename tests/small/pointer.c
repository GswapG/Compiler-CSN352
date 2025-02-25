#include <stdio.h>

int main(){
    int b = 1;
    int *p, a, *d = &b;
    p = &a;
    *p = 2;
    printf("a = %d, b = %d, *p = %d, *d = %d\n",a,b,*p,*d);
    int arr[5] = {1,2,3,4,5};
    int **np = &arr;
    for(int i = 0;i<5;i++){
        printf("arr[%d] = %d\n", i, **np);
        *np++;
    }
    return 0;
}