int func(int z, int k){
    return 1;
}

void hello(){
    int z = 1;
    z++;
}

int main() {
    int x,y = 2,z;
    if(x > 2){
        hello();
    }
    else if(y < (x++)){
        func(x,y);
    }
    // else if(z > 2){
    //     func(2,3);
    // }
    else{
        hello();
    }
}