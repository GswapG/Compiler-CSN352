int fucn(){
    return 1;
}
int main() {
    label:
        fucn()();
        char arr[5][15] = {'h', 6, 5.5};
        arr[14][5] = 5;
        goto label;
}