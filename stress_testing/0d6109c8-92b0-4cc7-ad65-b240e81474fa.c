struct hi{
  int i;
};
int fun(struct hi x,...){
  return x.i;
}
int main(){
  struct hi h;
  fun(h,1);
}