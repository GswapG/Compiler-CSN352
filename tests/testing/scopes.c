int* fun(int* i){
    return i;
 }
 int main(){
    int x = 4;
    int &f = x;
    int *g = &f;
    // int* a = fun(g);
    int ** ptr;
    ptr = &g;
    
 }