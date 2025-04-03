struct Data { int a; };
struct Data foo() { struct Data d; return d; }
int main() {
    struct Data d;
    d = foo();  // Valid
}