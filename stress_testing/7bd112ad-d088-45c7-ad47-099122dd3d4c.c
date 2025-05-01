#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    for(int i = 0;i<10;i++){
        if ( i%2==0){
            continue;
        }
        else{
            break;  
        }
    }
}
