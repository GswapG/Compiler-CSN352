int main() {
    int x=5;
    int *ptr=&x;
    int **ptr2=&ptr;
    int c = **ptr2+1;
    **ptr2 = 1;
}