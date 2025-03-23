/* Define a simple struct with typedef */
typedef struct {
    int x;
    int y;
} Point;

struct P2{
    int x;
    int y;
};

int f(float a , int b){
    float ALPHA = -1.0;
    return b+1;
}
int main() {
    Point p1;
    p1.x = 10;
    struct P2 gang;
    gang.x = 20;
    int y = 10;
    int abc2 = 10 + 20 + y;
    int abc = p1.x - gang.x;
    // p1.zz=10;
    int c = f(1.1,1);
}