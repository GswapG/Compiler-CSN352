#include <stdio.h>
#include <stdlib.h>

int main() {
    int value = 100;
    int *p1 = &value;
    int **p2 = &p1;
    int ***p3 = &p2;
    
    printf("Value via multi‑level pointers: %d\n", ***p3);
    
    // Create a 2D array using dynamic memory allocation
    int n = 5;
    int **arr = (int **)malloc(n * sizeof(int *));
    for(int i = 0; i < n; i++) {
        arr[i] = (int *)malloc(n * sizeof(int));
        for(int j = 0; j < n; j++) {
            arr[i][j] = i * n + j;
        }
    }
    
    // Print matrix using pointer arithmetic
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < n; j++) {
            printf("%d ", *(*(arr + i) + j));
        }
        printf("\n");
    }
    
    for(int i = 0; i < n; i++) {
        free(arr[i]);
    }
    free(arr);
    
    return 0;
}
