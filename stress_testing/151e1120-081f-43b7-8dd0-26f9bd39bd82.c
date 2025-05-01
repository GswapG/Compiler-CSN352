int three(void) {
    return 3;
}

int main(void) {
    return !three();
}

int expect_null_param(int *val)
{
    return (val == 0);
}

long *return_null_ptr(void)
{
    return 0; // convert return value to pointer
}