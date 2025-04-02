int func(int a, int b, ...) {
    return 5;
}

int main() {
    int x = 2;
    int z = func(x, x, 5);

    if (z == 5) {
        z = 3;
    } else {
        z = 4;
    }
}