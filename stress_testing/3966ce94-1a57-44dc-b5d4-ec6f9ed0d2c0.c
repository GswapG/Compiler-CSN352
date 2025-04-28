int func(int a, int b) {
	// return a + b;
	return 1;
}

int main(){
	int a = 1;
	int b = 2;
	int c = func(a, b);
	int arr[2];
	arr[0] = func(a, b);
	if (c != 3) {
		return 1; // Test failed
	}
	return 0; // Test passed
}
