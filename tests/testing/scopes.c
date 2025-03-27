struct Node {
    int height;
    char* name;
};

struct Node factorial(struct Node* A){
    struct Node m = *A;
    return m;
}

int main(){
    struct Node n;
    const struct Node D = factorial(&n);
	struct Node E = {5, "hello"};

	int x = 16;
	struct Node F = {x, E.name};

	char* name = "what";
	struct Node G = {E.height, name};

	const struct Node* ptr = &n;
	struct Node* ptr2;

	ptr = ptr2;
	// *ptr = D;
	// *ptr = F;

	// D = *ptr;
	// D = *ptr2;
}	