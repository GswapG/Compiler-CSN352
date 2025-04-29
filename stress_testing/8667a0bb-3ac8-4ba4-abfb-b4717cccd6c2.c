int main()
{
    int x=10;
    int *ptr = &x;
    int **ptr2 = &ptr;
    // ptr = ptr+x ;
    x = *ptr;
    *ptr=*ptr;
    printf("%d\n", x);
}