int main() {
    int x=5;
    int *p = &x;
    int **q= &p;
    int *(*pp)=&p;
    return 0;
}