struct A{
    int a;
    int b;
};
int main() {
    struct A a = {1,2};
    struct A b = {3,2};
    struct A arr[2] = {a,b};
}
