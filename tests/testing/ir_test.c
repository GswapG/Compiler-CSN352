struct s{
    int x;
    int g;
    struct gg{
        int ghh;
        int b;
    };
    struct gg h;
    int kk;
};

int main(){
    struct s p;
    p.h.b = 1;
}