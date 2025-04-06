#include <stdio.h>

int recursive_counter(int n) {
    static int count = 0;
    count++;
    return recursive_counter(n - 1);
}

int main() {
    recursive_counter(10);
    return 0;
}
