#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *fp = fopen("test.txt", "w");
    if(!fp) {
        printf("Failed to open file for writing.\n");
        return 1;
    }
    fprintf(fp, "Hello, file!\n");
    fclose(fp);
    
    fp = fopen("test.txt", "r");
    if(!fp) {
        printf("Failed to open file for reading.\n");
        return 1;
    }
    char buffer[50];
    fgets(buffer, sizeof(buffer), fp);
    printf("File content: %s", buffer);
    fclose(fp);
    
    return 0;
}
