typedef struct {
    int x;
    int y;
} floata;

struct Rectangle {
    floata topLeft;
    floata bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(floata p, floata q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize floatas using aggregate initialization */
    floata p1 = {10, 100};
    floata p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above floatas */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}