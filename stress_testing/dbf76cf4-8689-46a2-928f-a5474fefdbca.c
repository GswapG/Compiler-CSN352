int fucn(int x){
    return 1;
}
int main() {
    int arr[10][4][3];
    arr[2][3][4] = 2;
    fucn(arr[1][2][3]);
}