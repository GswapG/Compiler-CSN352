struct Node {
    int a;
    int b;
};

int main() {
    int x = 10;
    struct Node m = {x, 5};
    struct Node n = (struct Node)m;
}