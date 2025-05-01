// Test that we correctly get the size of ++ and -- expressions (and don't evaluate them)
int main(void) {
    int i = 0;
    long l = 0;
    static char arr[3] = {0, 0, 0};
    char *ptr = arr;
    if (sizeof (i++) != 4) {
        return 1; // fail
    }

    if (sizeof (arr[0]--) != 1) {
        return 2; // fail
    }

    if (sizeof (--arr[1]) != 1) {
        return 4; // fail
    }
}