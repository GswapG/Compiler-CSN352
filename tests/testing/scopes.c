int* fun(int i){
  return &i;
}

int main(int argc , char* argv[]){
  int x = 4;
  int f = x;
  int *g ;
  int k = -1;
  int **ptr;
  *ptr = g;
  *ptr = fun((**ptr * (*g))*99 + 11);
  if (**ptr + k <= 11 + 17*(*g) - 1){
    while(f < 77){
      f++;
      for(int i = 0;i<100;i+=3){
        //ignore
      }
    }
  }
}