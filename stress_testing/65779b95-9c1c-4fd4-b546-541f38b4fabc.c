#include <stdio.h>

int main() {
    int a = 5;
    int &refA = a; // reference variable
    refA += 10;
    printf("a = %d\n", a); // Should print 15
    
    int arr[3] = {1, 2, 3};
    for (int i = 0; i < 3; i++) {
        int &refElem = a;
        refElem *= 2;
    }
    printf("Doubled array: %d %d %d\n", arr[0], arr[1], arr[2]);
    
    return 0;
}
