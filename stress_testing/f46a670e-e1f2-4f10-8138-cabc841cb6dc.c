struct Node {
    int x;
    char c;
};

struct Point {
    int y;
};

int main() {
    int y = 10;
    void* x = (int*) &y;
    char c = 1;
    
    struct Node n = {y, 'c'};
    struct Point p = {y};
    void* ptr = (struct Node*) &n;
}