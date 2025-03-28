int main() {
    int c = 6;
    int* x = &c;
    unsigned int* f = (const unsigned int*)(x);
}