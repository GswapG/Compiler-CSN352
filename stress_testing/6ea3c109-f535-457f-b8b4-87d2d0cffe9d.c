struct Node {
    int x;
    char c;
};

int main() {
    int y = 10;
    void* x = (int*) &y;

    struct Node n = {y, 'c'};
    int* ptr = (void*) &n;
}