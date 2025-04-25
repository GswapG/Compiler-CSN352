#define int long long
void func(int a);

int func1(int a){
	return a;
}
signed main(){
	int x = 1;
	int y = 2;
	int z = x;
	y = z;
}
void func(int a){
	a = 1;
}