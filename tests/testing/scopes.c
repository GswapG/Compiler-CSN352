struct Node {
    const int x;
};
struct Other {
    int x;
};

int main() {
    struct Node n = {10};
    struct Other p;
    struct Node o = n;
    p.x -= p.x;

}