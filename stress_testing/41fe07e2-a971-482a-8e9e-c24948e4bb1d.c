typedef struct {
    int x;
    int y;
} Point;

struct P2 {
    int x;
    int y;
} ;

int main() {
    struct P2 p;
    struct P2 q = {5, 4};
    struct P2* p1 = &p;
    struct P2 A[2] = {p, q};

}