int func(int a, int b, ...) {
    return a;
}

int main() {
    int x = 2;
    int z = func(x, x, 5);
}