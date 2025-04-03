int func(int z, int k){
    return 1;
}

void hello(){
    int z = 1;
    z++;
}
int main() {
    int i = 1;
    int z;
    for(;;){
        z = func(4,3);
    }
    for(int x = 1;;){
        z = func(2,3);
    }
    for(;z<10;){
        z = func(10,3);
    }
    for(;;z++){
        z = func(3,100);
    }
    for(int x = 1;x < 100;){
        hello();
    }
    for(int x = 1;;z++){
        hello();
    }
    for(;z < 10;z++){
        hello();
    }
    for(int x = 1;x<100;i++){
        z = func(1,2);
    }
}