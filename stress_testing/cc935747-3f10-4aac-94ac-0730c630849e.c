int main()
{
    int x=10;
    int y=20;
    int *ptr = &y;
    int **ptr2 = &ptr;
    *ptr2 = ptr-1;
    x = *ptr;
    *ptr=*ptr;
    printf("%d\n", x);
}