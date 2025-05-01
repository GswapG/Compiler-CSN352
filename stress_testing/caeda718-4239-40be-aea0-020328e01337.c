// It's illegal to dereference a label
int main(void) {
	int x;
    lbl:
    *lbl;
    return 0;
}