int printf(const char* c, ...) {

}

int main() {
    const char c = 'c';
    char* d = "hellol";
    d = "hel";

    char **e = &d;

    const char* f = "hi";
    const char **e_ = &f;
    // const char **e__ = &d;
    char **e___ = &d;
    // char **e____ = &f;

    int result = printf(d, 1, 5.5);
}