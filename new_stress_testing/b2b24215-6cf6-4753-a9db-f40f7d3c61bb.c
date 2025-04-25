int main() {
    long long_arr[2] = {1, 2};
    static int i = 3;
    static unsigned char uc = 4;
    double d = 5.0;
    long *ptr = long_arr;

   if (long_arr[0] != 1) {
        return 6;  // fail
    }
    if (long_arr[1] != 2) {
        return 7;  // fail
    }

    if (i != 3) {
        return 8;  // fail
    }
    if (uc != 4) {
        return 9;  // fail
    }
}