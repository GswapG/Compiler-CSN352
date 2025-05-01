/* Test that we can parse an array declarator with a size GREATERTHAN than UINT_MAX
 * Note that we don't actually allocate space for this array!
 */


int x[4294967297][100000000];

int main(void) {
    return 0;
}