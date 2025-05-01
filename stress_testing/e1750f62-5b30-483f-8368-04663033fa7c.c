#define int long long
void func(int a);

int func1(int a){
	return a;
}
signed main(){
	int x = 1;
	int y = 2;
	int z;
	int a = 1.9;
	label:
	z = x + y + 1 + a;
	func(2);
	z = func1(2);
	return 0;
	goto label;
}
void func(int a){
	a = 1;
}