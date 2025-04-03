typedef struct {
   int x;
   int y;
} Point;

struct Rectangle {
   Point left;
   Point right;
};

int computeArea(Point p1, Point p2) {
   int height = p1.x - p2.x;
   int width = p1.y - p2.y;
   return height * width;
}

int main() {
   Point p1 = {10, 20};
   Point p2 = {30, 40};

   struct Rectangle rect = {p1, p2};
   int area = computeArea(rect.left, rect.right);
}