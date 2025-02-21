/* Start of large comment
   /* Nested comment - should be handled correctly */
   Another comment line
*/
int main() {
    int a = 0;
    for (int i = 0; i < 1000000; i++) { 
        a += i; 
    }
    return a;
}
