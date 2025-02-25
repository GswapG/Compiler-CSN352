#include <stdio.h>
#include <stdlib.h>

union Number {
    int i;
    float f;
};

int main() {
    FILE *fp = fopen("test.txt", "w+");
    if (!fp) {
        printf("Failed to open file.\n");
        return 1;
    }
    
    int count = 0;
    // do-while: write numbers to file
    do {
        fprintf(fp, "Number: %d\n", count);
        count++;
    } while (count < 5);
    
    rewind(fp);
    char line[100];
    // Custom until loop: read lines until fgets returns NULL
    do {
        printf("%s", line);
    } until(fgets(line, sizeof(line), fp) == NULL);
    
    fclose(fp);
    
    // Use union for demonstration
    union Number num;
    num.f = 3.14;
    printf("Union holds: %f\n", num.f);
    
    return 0;
}
