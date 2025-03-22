/* Define a simple struct with typedef */
typedef struct {
    int x;
    int y;
} Point;

// /* Define a struct that uses a nested struct */
struct Rectangle {
    Point topLeft;
    Point bottomRight;
};

// // /* A function that takes a struct as a parameter and returns its area */
int area(struct Rectangle rect) {
    // int width = rect.bottomRight.x - rect.topLeft.x;
    // int height = rect.bottomRight.y - rect.topLeft.y;
    // return width * height;
}

// int main() {
//     /* Initialize Points using aggregate initialization */
//     Point p1 = {10, 20};
//     Point p2 = {30, 40};

//     /* Initialize a Rectangle struct using the above Points */
//     struct Rectangle rect = {p1, p2};

//     /* Print the points and the rectangle area */
//     printf("Point p1: (%d, %d)\n", p1.x, p1.y);
//     printf("Point p2: (%d, %d)\n", p2.x, p2.y);
//     printf("Rectangle top left: (%d, %d), bottom right: (%d, %d)\n",
//            rect.topLeft.x, rect.topLeft.y, rect.bottomRight.x, rect.bottomRight.y);
//     printf("Area of rectangle: %d\n", area(rect));

//     return 0;
// }
