int func(int a, int b){
    int z;
    return z+1;
}
void this(){
    int a;
}
int main(){
labal:
    int x,y;
    x = x+y;
    int z = func(2,x*y);
    this();
    goto labal;
}
