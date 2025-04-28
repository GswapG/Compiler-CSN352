int main(){
	int x = 4;
	int *p = &x;

	*(p + 1) = *p + 1;
}