struct A{
    int x;
    double y;
    char z;
};
void func();
int main() {
    struct A a;
    a.x = 2;
    while(a.y){
        func();
    }  
}