struct A{
    int x;
    int y;
};

void fun(struct A a){
    a.x++;
}

int main() {
    struct A a;
    fun(a);
}
