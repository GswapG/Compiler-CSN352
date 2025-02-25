#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char str[50];
    int numbers[5];
    int sum = 0;
    
    printf("Enter a string: ");
    scanf("%49s", str);
    printf("You entered: %s\n", str);
    
    int i = 0;
    while(i < 5) {
        printf("Enter number %d: ", i+1);
        scanf("%d", &numbers[i]);
        i++;
    }
    
    i = 0;
    // do‑while to sum numbers
    do {
        if(numbers[i] < 0) {
            goto negative_error;
        }
        sum += numbers[i];
        i++;
    } while(i < 5);
    
    printf("Sum of numbers: %d\n", sum);
    return 0;
    
negative_error:
    printf("Error: Negative number encountered!\n");
    return 1;
}
