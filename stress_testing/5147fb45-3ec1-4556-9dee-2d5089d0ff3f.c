int main()
{
    // int x=10;
    // int y=20;
    // int *ptr = &y;
    // int **ptr2 = &ptr;
    // *ptr2 = ptr;
    // // *ptr2 = ptr;
    // x = *ptr;
    // *ptr=*ptr;
    int arr[10][10];
    arr[0][1] = 1;
    arr[1][0] = 1;
    printf("%d\n", arr[0][1]);
    printf("%d\n", arr[1][0]);
}