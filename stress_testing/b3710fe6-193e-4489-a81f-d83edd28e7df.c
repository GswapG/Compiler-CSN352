union Data {
    int i;
    float f;
};

int main() {
    union Data d;
    d.i = 100;
    d.f = 3.14;
    return 0;
}