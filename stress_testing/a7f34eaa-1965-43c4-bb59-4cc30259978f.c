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

    struct Node n = {y, 'c'};
    struct Point p = {y};
    int* ptr = (int*) &y;
}