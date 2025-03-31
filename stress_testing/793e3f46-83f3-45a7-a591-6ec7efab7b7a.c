int main() {
    int arr[10];
    int *p1;
    const int *p2;
    int diff = p1 - p2;  // Allowed! This computes how many elements apart they are.
}