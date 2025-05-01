int main(){
	int x = 4;
	int *p = &x;
	int *q;
	*(p + 1) = *p + *q;
}