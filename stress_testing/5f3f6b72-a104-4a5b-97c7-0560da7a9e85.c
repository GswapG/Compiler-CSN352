struct point{
    int x;
    int y;
};

struct Rectangle {
    struct point topLeft;
    struct point bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(struct point p, struct point q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize struct points using aggregate initialization */
    struct point p1 = {10, 100};
    struct point p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above points */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}