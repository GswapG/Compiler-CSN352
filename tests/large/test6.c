#include <stdio.h>

int recursive_counter(int n) {
    static int count = 0;
    count++;
    if(n <= 0) {
        printf("Total recursive calls (static): %d\n", count);
        return 0;
    }
    return recursive_counter(n - 1);
}

int main() {
    recursive_counter(10);
    return 0;
}
