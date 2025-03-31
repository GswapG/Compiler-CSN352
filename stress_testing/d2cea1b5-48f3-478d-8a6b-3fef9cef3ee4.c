struct Node {
    char c;
};

int main() {
    struct Node p, q, r;
    struct Node A[3] = {p, q};
    A[0] = r;
}