int main(){
    int l = 0;
    int r = 90000;
    int mid;
    while(l<=r){
        mid = l + (r-l)/2;
        if(mid*mid<=90000){
            l = mid+1;
        }
        else{
            r = mid-1;
        }
    }
    printf("%d",r);
    return 0;
}

() ? () : ()