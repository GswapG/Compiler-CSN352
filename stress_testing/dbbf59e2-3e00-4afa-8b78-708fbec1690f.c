int fun(int k, int* i, int** j){
   return fun(*i, i, &i);
}
int main(){
   int x = 4;
   int &f = x;
   int *g = &f;
   int a = fun(*g, g, &g);
}