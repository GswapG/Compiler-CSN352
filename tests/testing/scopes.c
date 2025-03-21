struct test {
    const int a = 5;
    float f;
    char c;
};

union hello {
    int b;
    char d;
    float f;
};

int main() {
    struct test t;
    t.c = 'a';
    t.f = 5.5;
    t.a = 10;

    union hello u;
    u.d = 'a';
    u.b = 100;
    u.f = 5.5;
    t.f = 10.6;
}   

