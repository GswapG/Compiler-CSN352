int func(int a, int b){
    int x = 0;
    int y = 2;
    printf("a is %d", 7);
    printf("b is %d", b);
    return a + b + x + y;
}

int main(){
    int x = func(1,2);
    printf("x is %d", x);
}