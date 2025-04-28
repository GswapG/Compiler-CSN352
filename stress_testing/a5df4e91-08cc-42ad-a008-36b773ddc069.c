int main(){
	int x =  1;
	int * ptr = &x;
	*ptr = *ptr + 2;
	*ptr= *ptr + *ptr;
}
