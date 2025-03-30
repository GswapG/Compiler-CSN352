struct Node { int value; };

int main() {
    struct Node n;
    struct Node *ptr = &n;
    ptr->value = 5;  // Valid
    n->value = 5;  // Invalid, struct is not a pointer
}
