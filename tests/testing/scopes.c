/* Define a simple struct with typedef */
struct Point{
    int x;
    int y;
};

struct {
    int x;
    int y;
}P2;

// /* Define a struct that uses a nested struct */
// struct Rectangle {
//     Point topLeft;
//     Point bottomRight;
// };

int main() {
    struct P2 p1;
    struct Point p2;
    p2.x = 0;
    // int a = p1.x - p2.x;
}
