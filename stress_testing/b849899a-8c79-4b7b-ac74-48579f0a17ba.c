union Data {
    int i;
    float f;
};

int main() {
    union Data d;
    d.i = 100;
    // printf("Unioninteger:%d\n", d.i);
    d.f = 3.14;
    // printf("Unionasfloat:%f\n", d.f);
    return 0;
}