struct Node {
    int x;
    char c;
};

union Point {
    int y;
};

int main() {
    int y = 10;
    void* x = (int*) &y;
    char c = 1;
    
    struct Node n = {y, 'c'};
    union Point p = {y};
    void* ptr = (union Point*) &p;
}