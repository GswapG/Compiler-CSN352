struct Node {
    char c[5];
};

struct Point {
    struct Node* ptr;
};

int main() {
    struct Node p, q, r;

    struct Point w;
    struct Node A[3] = {p, q};
    A[0] = r;

    struct Node* B[4] = {&p, &q, &w};
}