int main(){
    int a = 10, b = 3;
    int sum = a + b;          
    int diff = a - b;         
    int prod = a * b; 
    int eq  = (a == b);       // equality
    int ne  = (a != b);       // not equal
    int lt  = (a < b);        // less than
    int gt  = (a > b);        // greater than
    int le  = (a <= b);       // less than or equal to
    int ge  = (a >= b);       // greater than or equal to
    printf("Arithmetic:\n");
    printf("a + b = %d\n", sum);
    printf("a - b = %d\n", diff);
    printf("a * b = %d\n", prod);
    printf("Relational:\n");
    printf("a == b: %d\n", eq);
    printf("a != b: %d\n", ne);
    printf("a < b:  %d\n", lt);
    printf("a > b:  %d\n", gt);
    printf("a <= b: %d\n", le);
    printf("a >= b: %d\n\n", ge);
}
