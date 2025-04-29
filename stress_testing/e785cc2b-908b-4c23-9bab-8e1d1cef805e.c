int main()
{
    int x=10;
    int y=20;
    int *ptr = &x;
    int **ptr2 = &ptr;
    ptr = ptr-1;
    x = *ptr;
    *ptr=*ptr;
    printf("%d\n", x);
}