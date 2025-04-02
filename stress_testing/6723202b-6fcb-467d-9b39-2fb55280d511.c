int func(){
    int x;
}
int main() {
    int result;
    int x = 7;
    func();
    switch (x) {
        case 1:
            result = 1;
            int y = 2;
            break;
        default:
            result = 60;  // Default case
            break;
    }
    int endMarker = 99;  // End of switch block marker
}