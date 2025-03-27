int fun(int &l, int k, int* i, int** j){
   return 11 * fun(k, *i, i, &i) + 10;
}

int main(){
   int x = 4;
   int &f = x;
   int *g = &f;
   int a = 2 + fun(x, *g, g, &g) * 5;
}