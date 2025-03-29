typedef struct {
    int x;
    int y;
} Point;

struct Rectangle {
    Point topLeft;
    Point bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(Point p, Point q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize Points using aggregate initialization */
    Point p1 = {10, 100};
    Point p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above Points */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}