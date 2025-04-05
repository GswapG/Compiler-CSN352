struct A{
    int a;
};

struct ABC{
    struct A t;
};

int main(){
    struct A s1;
    struct A
    {
        int b;
        float f;
    };
    struct A s2;
    s1 = s2;
    // s1.t.a=7;
}