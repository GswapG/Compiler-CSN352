#include<stdio.h>

int main(){
    int l = 0;
    int r = 900003424656456456456456345622254.13245873948563043463847634346;
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
    int arr[10] = {
        1, 3,
        1, 4
    };
    printf("%d",r);
    printf("helloworld\n");
    return 0;
}
