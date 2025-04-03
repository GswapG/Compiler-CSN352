struct Point { int x, y; };

int main() {
	int arr[10];
    int a = arr[5];  // Valid
    float b = arr[2]; // Valid (implicit conversion)
    char c = arr[7];  // Valid but should trigger a type mismatch warning


}