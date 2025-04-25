int main() {
    int* ptr;
    if (sizeof(ptr += 1)) {
        return 5;  // fail
    }
}