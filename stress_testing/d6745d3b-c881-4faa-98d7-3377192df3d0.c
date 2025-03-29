enum Color {TRUE, FALSE};

int main() {
    int** x;
    int y = **x;
    y += **x + y;
}