struct Node {
    int x;
    int* p;
};

int main() {
    int x = 2; 
    struct Node n = {x, &x};
}