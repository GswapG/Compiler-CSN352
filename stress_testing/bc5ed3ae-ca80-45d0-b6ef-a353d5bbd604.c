// compound bitwise assignment on subscript expressions
int main(void) {
    unsigned long arr[4] = {
        2147483648,                // 2^32
        18446744069414584320,     // 0xffff_ffff_0000_0000
        9223372036854775808,      // 2^63,
        1085102592571150095        // 0x0f0f_0f0f_0f0f_0f0f
    };

    // &=
    arr[1] &= arr[3];
    if (arr[1] != 1085102592318504960 /* 0x0f0f_0f0f_0000_0000 */) {
        return 1;
    }

    // |=
    arr[0] |= arr[1];
    if (arr[0] != 1085102594465988608) {
        return 2;
    }

    // ^=
    arr[2] ^= arr[3];
    if (arr[2] != 10308474629425925903) {
        return 3;
    }

    // >>=
    arr[3] >>= 25;
    if (arr[3] != 32338577287) {
        return 4;
    }

    // <<=
    arr[1] <<= 12;
    if (arr[1] != 17361640446303928320) {
        return 5;
    }

    return 0; // success
}