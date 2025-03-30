struct Data { int a; };
struct Data foo() { struct Data d; return d; }
int main() {
    int *p;
    *p = 10;

    int **pp;
    **pp = 20; 

    int ***ppp;
    ***ppp = 30;

    int ****q;
    ****q = 5;
}