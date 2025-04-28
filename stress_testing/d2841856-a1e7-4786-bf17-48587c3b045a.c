/* Test initialzing one-dimensional arrays with automatic storage duration */

/* Initialize array with three constants */
int test_simple(void) {
    unsigned long arr[3] = {18446744073709551615, 9223372036854775807,
                            100};

    return (arr[0] == 18446744073709551615 &&
            arr[1] == 9223372036854775807 && arr[2] == 100);
}

/* if an array is partially initialized, any elements that aren't
 * explicitly initialized should be zero.
//  */
int test_partial(void) {
    double arr[5] = {1.0, 123};

    // make sure first two elements have values from initializer and last three
    // are zero
    return (arr[0] == 1.0 && arr[1] == 123.7 && !arr[2] && !arr[3] && !arr[4]);
}

// /* An initializer can include non-constant expressions, including function
//  * parameters */
// int test_non_constant(long negative_7billion, int *ptr) {
//     *ptr = 1;
//     extern int three(void);
//     long var = negative_7billion * three();  // -21 billion
//     long arr[5] = {
//         negative_7billion,
//         three() * 7,                      // 21
//         -(long)*ptr,                       // -1
//         var + (negative_7billion ? 2 : 3)  // -21 billion  + 2
//     };  // fifth element  not initialized, should be 0

//     return (arr[0] == -7000000000 && arr[1] == 21 && arr[2] == -1 &&
//             arr[3] == -20999999998 && arr[4] == 0);
// }

// // helper function for test case above
// int three(void) {
//     return 3;
// }

// long global_one = 1l;
// /* elements in a compound initializer are converted to the right type as if by
//  * assignment */
// int test_type_conversion(int *ptr) {
//     *ptr = -100;

//     unsigned long arr[4] = {
//         3458764513821589504.0,  // convert double to ulong
//         *ptr,  // dereference to get int, then convert to ulong - end up with
//                // 2^64 - 100
//         (unsigned int)18446744073709551615,  // this is ULONG_MAX - truncate
//                                                // to unsigned int, then back to
//                                                // ulong, end up with UINT_MAX
//         -global_one                            // converts to ULONG_MAX
//     };

//     return (arr[0] == 3458764513821589504 &&
//             arr[1] == 18446744073709551516 && arr[2] == 4294967295 &&
//             arr[3] == 18446744073709551615);
// }

// /* Initializing an array must not corrupt other objects on the stack. */
// int test_preserve_stack(void) {
//     int i = -1;

//     /* Initialize with expressions of long type - make sure they're truncated
//      * before being copied into the array.
//      * Also use an array of < 16 bytes so it's not 16-byte aligned, so there are
//      * eightbytes that include both array elements and other values.
//      * Also leave last element uninitialized; in assembly, we should set it to
//      * zero without overwriting what follows
//      */
//     int arr[3] = {global_one * 2, global_one + three()};
//     unsigned int u = 2684366905;

//     // check surrounding objects
//     if (i != -1) {
//         return 0;
//     }
//     if (u != 2684366905) {
//         return 0;
//     }

//     // check arr itself
//     return (arr[0] == 2 && arr[1] == 4 && !arr[2]);
// }

// int main(void) {
//     if (!test_simple()) {
//         return 1;
//     }

//     if (!test_partial()) {
//         return 2;
//     }

//     long negative_seven_billion = -7000000000;
//     int i = 0;  // value of i doesn't matter, functions will always overwrite it
//     if (!test_non_constant(negative_seven_billion, &i)) {
//         return 3;
//     }

//     if (!test_type_conversion(&i)) {
//         return 4;
//     }

//     if (!test_preserve_stack()) {
//         return 5;
//     }

//     return 0;  // success
// }