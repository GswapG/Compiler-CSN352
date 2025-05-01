int main(){
	int x = 4;
	int*p = &x;
	*(p + 4) = *(p + 4);

}