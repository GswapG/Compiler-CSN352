struct Point {
    char* c;
    int y;
};

int main() {
    struct Point p = {"hello", 20};
    struct Point q = {"hello", p.y};
}