int func(char x, char y, int z);

int func(char x, char y, int z) {
    x = 5;
    return y;
} 


int main() {
    int a = func('a', 'b', 5);
}