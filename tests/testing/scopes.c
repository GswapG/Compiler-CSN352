struct Point {
    int x;
    int y;
};

struct Rectangle {
    struct Point topLeft;
    struct Point bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(struct Point p, struct Point q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize Points using aggregate initialization */
    struct Point p1 = {10, 20};
    struct Point p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above Points */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}