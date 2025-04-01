int main() {
    int a = 1, b = 0;
    if (a && b) {
        // label:
        a = 2;
    }
    goto label;
}
