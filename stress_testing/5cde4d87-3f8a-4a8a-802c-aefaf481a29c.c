struct Node{
    int a;
    int b;
};

struct Node factorial(struct Node n) {
    struct Node m = n; 
    m.a = 1; //this line causes error !!
    m.b = 1; //same here  
    return m;
}

int main() {
    struct Node n = {5, 10}; // This line causes error
    return 0;
}