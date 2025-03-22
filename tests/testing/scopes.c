/* Define a simple struct with typedef */
// struct Point{
//     int x;
//     int y;
// };

// struct {
//     int x;
//     int y;
// }P2;

// /* Define a struct that uses a nested struct */
// struct Rectangle {
//     Point topLeft;
//     Point bottomRight;
// };

int main() {
    int a;
    int *ptr = &a;
    int **e = &ptr;
    int d;
    int c = a +  *ptr  - **e + d;   
    // int a = p1.x - p2.x;
}
