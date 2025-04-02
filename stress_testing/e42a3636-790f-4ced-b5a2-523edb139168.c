union A{
     int a;
     char c;
};
int main() {
     // char arr [11] = {1,2,3,4,5};
     // int x = a.d + 1;
     // a->d = 11;
     // int arr [5] = {1,23,11};
     union A a;
     a.a = 1;
     int *** ptr;
     **ptr = &a.a;
}