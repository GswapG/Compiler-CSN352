#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if(argc < 3) {
        printf("Usage: %s <inputfile> <outputfile>\n", argv[0]);
        return 1;
    }
    FILE *fin = fopen(argv[1], "r");
    if(!fin) {
        printf("Could not open input file.\n");
        return 1;
    }
    FILE *fout = fopen(argv[2], "w");
    if(!fout) {
        printf("Could not open output file.\n");
        fclose(fin);
        return 1;
    }
    
    char buffer[256];
    while(fgets(buffer, sizeof(buffer), fin)) {
        fputs(buffer, fout);
    }
    
    fclose(fin);
    fclose(fout);
    printf("File copy completed.\n");
    return 0;
}
