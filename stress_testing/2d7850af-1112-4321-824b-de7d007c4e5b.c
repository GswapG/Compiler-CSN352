
// // helper function for previous test
unsigned int three(void) {
    return 3;
}

// /* Initializing an array must not corrupt other objects on the stack. */
long one = 1;
int test_preserve_stack(void) {
    int i = -1;

    /* Initialize with expressions of long type - make sure they're truncated
     * before being copied into the array.
     * Also use an array of < 16 bytes so it's not 16-byte aligned, so there are
     * quadwords that include both array elements and other values.
     * Also leave last element uninitialized; in assembly, we should set it to
     * zero without overwriting what follows
     */
    int arr[3][1] = {{one * 2}, {one + three()}};
    unsigned int u = 2684366905;

    if (i != -1) {
        return 0;
    }

    if (u != 2684366905) {
        return 0;
    }

    // if (arr[0][0] != 2 || arr[1][0] != 4 || arr[2][0] != 0) {
    //     return 0;
    // }

    return 1;  // success
}

// int main(void) {
//     if (!test_simple()) {
//         return 1;
//     }

//     if (!test_partial()) {
//         return 2;
//     }

//     if (!test_non_constant_and_type_conversion()) {
//         return 3;
//     }

//     if (!test_preserve_stack()) {
//         return 4;
//     }

//     return 0;  // success
// }
