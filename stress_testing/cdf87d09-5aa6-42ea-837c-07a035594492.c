int main() {
    int i = 0;
    printf("%deven", i);
    for (int i = 0; i < 5; i++) 
    {
        if(i % 2 == 0) { 
            printf("%diseven", i); 
        }
        else { 
            printf("%disodd", i); 
        }    
    }
}