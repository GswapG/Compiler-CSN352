int main() {
    int a = 5;
    int *p = &a;
    int *q;
    q = p;
    *q = a;

    int **ptr;
    ptr = &q;
    *ptr = p;
    *ptr = q; //-> false negative
}