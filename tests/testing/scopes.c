struct Node {
    int x;
    int* p;
};

int main() {
    int x = 2; 
    int *p = &x;
    struct Node n = {*p, p};
}