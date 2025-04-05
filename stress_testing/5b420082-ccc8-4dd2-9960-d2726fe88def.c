int func(int x,int y){
    return 1;
}
int main(){
    int x,y;
    printf("%d",func(func(x,y),y));
}