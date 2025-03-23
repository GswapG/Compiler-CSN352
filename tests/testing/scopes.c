struct A { 
    int x;
    float f;
    char c;
};

struct B {
    int y;
    float g;
    char d;
};

int main() {
    struct A a = {1, 4.4};
    struct B b = {a.x, a.f};

}