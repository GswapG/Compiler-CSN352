// Pointer arithmetic with +=/-=

int i = 4;

int int_array(void) {
    
}

int double_array(void) {
    // identical to int_array but with static double array instead
    
}

int main(void) {
    int result;

    if ((result = int_array())) {
        return result; // int_array returned non-zero result - fail
    }
    if ((result = double_array())) {
        return result + 12; // double_array returned non-zero result - fail
    }
    return 0; // success
}