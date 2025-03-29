union Node {
    int f;
    double d;
    char c;
};

int main() {
    union Node n = {1, 4.4};
    int x = 5;
}