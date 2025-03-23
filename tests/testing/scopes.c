struct Node {
    const int x;
};
struct Other {
    int x;
};

int main() {
    struct Node n = {10};
    struct Node o = n;
    
    struct Node a[2] = {o, n};
}