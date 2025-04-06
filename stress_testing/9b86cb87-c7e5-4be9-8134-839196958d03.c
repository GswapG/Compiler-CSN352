typedef struct {
    int x;
    int y;
} asdasshortieasd;

struct Rectangle {
    asdasshortieasd topLeft;
    asdasshortieasd bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(asdasshortieasd p, asdasshortieasd q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize asdasshortieasds using aggregate initialization */
    asdasshortieasd p1 = {10, 100};
    asdasshortieasd p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above asdasshortieasds */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}