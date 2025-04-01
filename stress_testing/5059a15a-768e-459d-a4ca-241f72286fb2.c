struct Point {
    int x;
    float f;
    char c;
};

int func(const int x, char* ptr, char c, double d) {
    int y = x;
    struct Point p = {y, d, c};
    return func(x, ptr, c, d);
}

int main() {
    const unsigned int a = func(1, "hello", 'c', 5.5);
    struct Point p = {a, 5.5};
    struct Point q;

    struct Point *ptr = &q;
    struct Point A[3] = {p, q};
}