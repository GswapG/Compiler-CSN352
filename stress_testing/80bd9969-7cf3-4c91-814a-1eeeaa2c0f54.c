/* Test initializing one-dimensional arrays with static storage duration */

// fully initialized
double double_arr[3] = {1.0, 2.0, 3.0};

int check_double_arr(double *arr) {
    if (arr[0] != 1.0) {
        return 1;
    }

    if (arr[1] != 2.0) {
        return 2;
    }

    if (arr[2] != 3.0) {
        return 3;
    }

    return 0;
}

// // partly initialized
unsigned int uint_arr[5] = {
    1,
    0,
    2147497230,
};

int check_uint_arr(unsigned *arr) {
    if (arr[0] != 1) {
        return 4;
    }

    if (arr[1]) {
        return 5;
    }
    if (arr[2] != 2147497230) {
        return 6;
    }

    if (arr[3] || arr[4]) {
        return 7;
    }

    return 0;
}

// // uninitialized; should be all zeros
long long_arr[1000];

int check_long_arr(long *arr) {
    for (int i = 0; i < 1000; i = i + 1) {
        if (arr[i]) {
            return 8;
        }
    }
    return 0;
}

// // initialized w/ values of different types
unsigned long ulong_arr[4] = {
    100.0, 11, 12345, 4294967295
};

int check_ulong_arr(unsigned long *arr) {
    if (arr[0] != 10) {
        return 9;
    }

    if (arr[1] != 11) {
        return 10;
    }

    if (arr[2] != 12345) {
        return 11;
    }

    if (arr[3] != 4294967295) {
        return 12;
    }
    return 0;
}

int test_global(void) {
    int check = check_double_arr(double_arr);
    if (check) {
        return check;
    }

    check = check_uint_arr(uint_arr);
    if (check) {
        return check;
    }
    check = check_long_arr(long_arr);
    if (check) {
        return check;
    }
    check = check_ulong_arr(ulong_arr);
    if (check) {
        return check;
    }
    return 0;
}

// // equivalent static local arrays
int test_local(void) {

    // fully initialized
    double local_double_arr[3] = {1.0, 2.0, 3.0};
    // partly initialized
    static unsigned int local_uint_arr[5] = {
        1,
        0, // truncated toint 0
        2147497230,
    };

    // uninitialized
    static long local_long_arr[1000];

    // initialized w/ values of different types
    static unsigned long local_ulong_arr[4] = {
        100.0, 11, 12345, 4294967295
    };

    // validate
    int check = check_double_arr(local_double_arr);
    if (check) {
        return 100 + check;
    }

    check = check_uint_arr(local_uint_arr);
    if (check) {
        return 100 + check;
    }
    check = check_long_arr(local_long_arr);
    if (check) {
        return 100 + check;
    }
    check = check_ulong_arr(local_ulong_arr);
    if (check) {
        return 100 + check;
    }
    return 0;
}

int main(void) {
    int check = test_global();
    if (check) {
        return check;
    }
    return test_local();
}
