#include <stdio.h>
#include <stdlib.h>

int main() {
    int rows = 3, cols = 3;
    // Allocate matrices A, B, and C dynamically
    int **A = (int **)malloc(rows * sizeof(int *));
    int **B = (int **)malloc(rows * sizeof(int *));
    int **C = (int **)malloc(rows * sizeof(int *));
    for(int i = 0; i < rows; i++) {
        A[i] = (int *)malloc(cols * sizeof(int));
        B[i] = (int *)malloc(cols * sizeof(int));
        C[i] = (int *)malloc(cols * sizeof(int));
    }
    
    // Initialize A and B; zero initialize C
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++) {
            A[i][j] = i + j;
            B[i][j] = i * j;
            C[i][j] = 0;
        }
    }
    
    // Matrix multiplication: C = A * B
    for(int i = 0; i < rows; i++)
        for(int j = 0; j < cols; j++)
            for(int k = 0; k < cols; k++)
                C[i][j] += A[i][k] * B[k][j];
    
    printf("Matrix C (Result):\n");
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++)
            printf("%d ", C[i][j]);
        printf("\n");
    }
    
    for(int i = 0; i < rows; i++) {
        free(A[i]); free(B[i]); free(C[i]);
    }
    free(A); free(B); free(C);
    
    return 0;
}
