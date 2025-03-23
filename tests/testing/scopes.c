struct Node {
    const int x;
};
struct Other {
    int x;
};

int main() {
    struct Node n = {10};
    struct Other p = {5};
    struct Node o = n;
    n.x += p.x;

}