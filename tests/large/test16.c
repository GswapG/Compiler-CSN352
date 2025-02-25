#include <stdio.h>
#include <stdlib.h>

int** allocate_matrix(int rows, int cols) {
    int **matrix = (int **)malloc(rows * sizeof(int *));
    for(int i = 0; i < rows; i++)
        matrix[i] = (int *)malloc(cols * sizeof(int));
    return matrix;
}

void initialize_matrix(int **matrix, int rows, int cols) {
    for(int i = 0; i < rows; i++)
        for(int j = 0; j < cols; j++)
            matrix[i][j] = i * cols + j;
}

int main() {
    int rows = 4, cols = 4;
    int **mat = allocate_matrix(rows, cols);
    initialize_matrix(mat, rows, cols);
    
    for(int i = 0; i < rows; i++) {
        for(int j = 0; j < cols; j++)
            printf("%d ", mat[i][j]);
        printf("\n");
    }
    
    for(int i = 0; i < rows; i++)
        free(mat[i]);
    free(mat);
    
    return 0;
}
