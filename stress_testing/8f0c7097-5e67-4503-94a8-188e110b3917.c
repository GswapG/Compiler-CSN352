int expect_null_param(int *val)
{
    return (val == 0);
}

long *return_null_ptr(void)
{
    return 0; // convert return value to pointer
}

long *get_null_pointer(void) {
    return 0;
}

int main() {
	int *y;
	if (y != 0)
		return 5;

	int* ptr;
	int *ternary_result = 10 ? 0 : ptr;
    if (ternary_result) {
        return 8;
    }
}