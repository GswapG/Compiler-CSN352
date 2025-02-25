#include <stdio.h>
#include <stdlib.h>

typedef int (*func_ptr)(int);

int recursive_sum(int n) {
    if(n <= 0) return 0;
    return n + recursive_sum(n - 1);
}

int main() {
    func_ptr sum_func = recursive_sum;
    int num = 10;
    int result = sum_func(num);
    printf("Sum from 1 to %d is %d\n", num, result);
    
    typedef int ArrayType;
    ArrayType *arr = (ArrayType*)malloc(num * sizeof(ArrayType));
    if(!arr) {
        printf("Allocation failed.\n");
        return 1;
    }
    for(int i = 0; i < num; i++) {
        arr[i] = i;
    }
    printf("Array elements: ");
    for(int i = 0; i < num; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    free(arr);
    return 0;
}
