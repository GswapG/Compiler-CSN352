void func(int a){
	a = 1;
}
int func1(int a){
	return a;
}
int main(){
	int x1 = 1;
	int y = 2;
	int z;
	int a = 1.9;
	z = x1 + y + 1 + a;
	func(2);
	z = func1(2);
	return 0;
}