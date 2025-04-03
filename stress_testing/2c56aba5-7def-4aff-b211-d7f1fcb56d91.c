int main() {
    int x = 10;
    int* y = &x;
    int** w = &y;
    int **z = x + w;
}