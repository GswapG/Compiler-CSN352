struct Point { int x, y; };

struct Rectangle { float width, height; };

int main() {
    struct Point p;
    p.x = 10;  // Valid
    p.y = 20;  // Valid

    struct Rectangle rect;  
    // rect.area = 100;  // Invalid, area is not a member
}


