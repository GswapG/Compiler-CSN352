int main() {
    int x=5;
    int *ptr=&x;
    int c = *ptr+1;
    *ptr = 1;
}