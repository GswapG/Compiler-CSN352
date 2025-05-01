
int main(void) {
    unsigned int ui = -1; // lower 32 bits set
    unsigned long ul = 9223372036854775808; // 2^63, only uppermost bit set
    unsigned int *ui_ptr = &ui;
    unsigned long *ul_ptr = &ul;

    if ((*ui_ptr & *ul_ptr) != 0) {
        return 1;
    }

    if ((*ui_ptr | *ul_ptr) != 9223372041149743103) {
        return 2;
    }

    int i = -1;
    signed int *i_ptr = &i;
    if ((*i_ptr & ul) != *ul_ptr) {
        return 3;
    }

    if ((*i_ptr | *ul_ptr) != i) {
        return 4;
    }

    return 0; // success
}