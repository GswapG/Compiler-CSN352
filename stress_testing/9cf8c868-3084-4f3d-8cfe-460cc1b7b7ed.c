int main()
{
	int x=0;
	int *ptr = &x;
	int **ptr2 = &ptr;
	ptr = ptr+x ;
	x = *ptr;
	*ptr=*ptr;
}