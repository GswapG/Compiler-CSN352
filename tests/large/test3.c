#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef char* string;

int main(int argc, char *argv[]) {
    if(argc < 3) {
        printf("Usage: %s <word> <repeat>\n", argv[0]);
        return 1;
    }
    string word = argv[1];
    int repeat = atoi(argv[2]);
    int len = strlen(word);
    
    // Allocate a 2D array: repeat rows of (len+1) chars
    char **matrix = (char **)malloc(repeat * sizeof(char *));
    for (int i = 0; i < repeat; i++) {
        matrix[i] = (char *)malloc((len + 1) * sizeof(char));
        if (!matrix[i]) { 
            printf("Allocation failed\n"); 
            return 1;
        }
    }
    
    // Fill matrix with a pattern: normal in even rows, reversed in odd rows
    for (int i = 0; i < repeat; i++) {
        for (int j = 0; j < len; j++) {
            if(i % 2 == 0)
                matrix[i][j] = word[j];
            else
                matrix[i][j] = word[len - j - 1];
        }
        matrix[i][len] = '\0';
    }
    
    // Print and free matrix
    for (int i = 0; i < repeat; i++) {
        printf("%s\n", matrix[i]);
        free(matrix[i]);
    }
    free(matrix);
    
    return 0;
}
