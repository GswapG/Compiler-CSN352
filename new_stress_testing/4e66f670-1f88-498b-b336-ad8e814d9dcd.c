int main() {
    int x;
    int* p = &x;
    p -= 1;
    p += x;
    p++;
    p--;
    int* y = p + 5;
}