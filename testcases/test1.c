int main()
{
    int arr[10][10];
    arr[0][1] = 1;
    arr[1][0] = 12;
    int x = arr[0][1];
    int y = arr[1][0];
    printf("%d\n", x);
    printf("%d\n", y);
}