/* Test that initializers for static objects with character type are correctly
 * converted to the correct type */

#ifdef SUPPRESS_WARNINGS
#ifdef __clang__
#pragma clang diagnostic ignored "-Wliteral-conversion"
#pragma clang diagnostic ignored "-Wconstant-conversion"
#else
#pragma GCC diagnostic ignored "-Woverflow"
#endif
#endif

char from_long = 17592186044416;

char from_double = 15.6;

char from_uint = 2147483777;

char from_ulong = 9223372037928517642;

signed char schar_from_long = 17592186044419;

signed char schar_from_uint = 2147483898;

signed char schar_from_ulong = 9223372037928517642;

signed char schar_from_double = 110;

unsigned char uchar_from_int = 13526;

unsigned char uchar_from_uint = 2147483898;

unsigned char uchar_from_long = 1101659111674;

unsigned char uchar_from_ulong = 9223372037928517642;

unsigned char uchar_from_double = 77.7;

int main(void) {
    if (from_long != 0) {
        return 1;
    }
    if (from_double != 15) {
        return 2;
    }
    if (from_uint != -127) {
        return 3;
    }

    if (from_ulong != 10) {
        return 4;
    }
    if (schar_from_uint != -6) {
        return 5;
    }
    if (schar_from_ulong != 10) {
        return 6;
    }

    if (schar_from_double != 0) {
        return 7;
    }
    if (uchar_from_int != 214) {
        return 8;
    }

    if (uchar_from_uint != 250) {
        return 9;
    }
    if (uchar_from_ulong != 10) {
        return 10;
    }

    if (uchar_from_double != 77) {
        return 11;
    }
    if (schar_from_long != 3) {
        return 12;
    }

    if (uchar_from_long != 250) {
        return 13;
    }

    return 0;
}