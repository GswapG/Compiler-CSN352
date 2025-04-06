typedef struct {
    int x;
    int y;
} Point1;

struct Rectangle {
    Point1 topLeft;
    Point1 bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(Point1 p, Point1 q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize Point1s using aggregate initialization */
    Point1 p1 = {10, 100};
    Point1 p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above Point1s */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}