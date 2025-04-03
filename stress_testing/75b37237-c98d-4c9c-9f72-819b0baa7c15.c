int func(){
    return 1;
}
int main() {
    int z = 2;
    float f = 1.2;
    z = z + f;
    z *= 1.2;
    while(z>f){
        func();
    }
} 