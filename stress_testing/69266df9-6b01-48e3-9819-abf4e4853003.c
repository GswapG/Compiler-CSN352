int* func(int a, int b){
    int *p = &a;
    return p;
}

int main() {
    int* c = func(5, 6);
}