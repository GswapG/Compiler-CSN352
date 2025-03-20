struct test {
    int a;
    int b;
    char c;
    struct child {
        int c;
        char a;
    } declare;
};

union what {
    char a;
    int b;
};

int func(int a, int b) {
    b = 100;
    char c;
}

int main() {
    // primitive types
    int a;
}
