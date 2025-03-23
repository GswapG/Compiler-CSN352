struct Node {
    int x;
};
struct Other {
    int x;
};

int main() {
    struct Node n = {10};
    struct Other p;
    // struct Node o = p;
    p.x = n.x;

}