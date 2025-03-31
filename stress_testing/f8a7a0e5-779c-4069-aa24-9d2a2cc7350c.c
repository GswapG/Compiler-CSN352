struct Node {
    char c[5];
};

int main() {
    struct Node p, q, r;
    struct Node A[3] = {p, q};
    A[0] = r;

    r = A[1];
}