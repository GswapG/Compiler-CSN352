typedef struct {
    int x;
    int y;
} point;

struct Rectangle {
    point topLeft;
    point bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(point p, point q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize points using aggregate initialization */
    point p1 = {10, 100};
    point p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above points */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}