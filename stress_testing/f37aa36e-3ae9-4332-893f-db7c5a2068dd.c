typedef struct {
    int x;
    int y;
} aalongaa;

struct Rectangle {
    aalongaa topLeft;
    aalongaa bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(aalongaa p, aalongaa q) {
    int width = p.x - q.x;
    int height = p.y - q.y;
    return width * height;
}

int main(void) {
    /* Initialize aalongaas using aggregate initialization */
    aalongaa p1 = {10, 100};
    aalongaa p2 = {30, 40};

    // /* Initialize a Rectangle struct using the above aalongaas */
    struct Rectangle rect = {p1, p2};

    int area = computeArea(p1, p2);
}