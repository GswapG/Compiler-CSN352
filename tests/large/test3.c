#include <stdio.h>
#include <stdlib.h>
typedef int Matrix;

int main() {
    Matrix m[3][3] = {
        {1,2,3},
        {4,5,6},
        {7,8,9}
    };
    
    int *p = &m[0][0];
    static int counter = 0;
    
    // Print matrix using pointer arithmetic
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%d ", *(p + i*3 + j));
            counter++;
        }
        printf("\n");
    }
    
    if(counter != 9) {
        goto error;
    }
    return 0;
    
error:
    printf("Error: Matrix traversal failed.\n");
    return 1;
}
