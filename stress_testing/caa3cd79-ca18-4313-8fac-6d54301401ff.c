struct Node {
    int f;
    double d;
    char c;
};

int func(struct Node* arr) {
    return 4;
}

int main() {
    struct Node arr[4];
    int x = func(arr);
}