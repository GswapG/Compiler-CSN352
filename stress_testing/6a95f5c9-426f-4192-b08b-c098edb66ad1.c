struct floaata{
	int x;
	int y;
};

struct Rectangle {
	struct floaata topLeft;
	struct floaata bottomRight;
};

/* A function that takes a struct as a parameter and returns its area */
int computeArea(struct floaata p,struct floaata q) {
	int width = p.x - q.x;
	int height = p.y - q.y;
	return width * height;
}

int main(void) {
	/* Initialize floatas using aggregate initialization */
	struct floaata p1 = {10, 100};
	struct floaata p2 = {30, 40};

	// /* Initialize a Rectangle struct using the above floatas */
	// struct Rectangle rect = {p1, p2};

	int area = computeArea(p1, p2);
}