#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *fp = fopen("nonexistent.txt", "r");
    if(!fp) {
        goto file_error;
    }
    
    // (Assume file processing here)
    fclose(fp);
    return 0;
    
file_error:
    printf("Error: Could not open file.\n");
    return 1;
}
