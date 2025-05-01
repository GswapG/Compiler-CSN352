int main(){
    int i = 0;
    int j = 10;
    while(i < j){
        if(i >= j){
            printf("i is less than j\n");
        }
        else{
            printf("j is less than i\n");
            break;
        }
        i = i + 1;
    }
    printf("Outside loop");
}