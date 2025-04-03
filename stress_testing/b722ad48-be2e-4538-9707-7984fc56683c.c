struct Point { int x, y; };

int add(int a, int b) { return a + b; }


float square(float x) { return x * x; }


int foo(int a) { return a; }



int main() {
	int arr[10];
    int sum = add(2, 3);  // Valid

    float result = square(4.5);  // Valid

    // int res = foo();  // Invalid, missing argument
}