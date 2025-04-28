int func(int a, int b) {
	return a + b;
}
int main(){
	int a = 1;
	int b = 2;
	int c = func(a, b);
	if (c != 3) {
		return 1; // Test failed
	}
	return 0; // Test passed
}