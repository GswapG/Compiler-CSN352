typedef struct{
    const int x;
} Node;

struct Node2 {
    int x;
};

int main() {
    Node n = {};
    Node p = {1};

    Node a[2] = {n, p};
}