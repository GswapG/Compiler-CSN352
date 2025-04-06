struct test{
    int a[3];
    // long long b;
};
// int main(int argc , char *argv[]){
//     argv[0] = "hello";
//     *(argv+ 'x') = "hello";
//     int arr[10];
//     arr[1] = 0;
//     int * p;
//     return 0;
// }
int main(){
    struct test t;
    *(t.a + 5) =1;
    // int arr[10][20][30];
    // int x=arr[1][2][3];
    // t.b = 1;
}