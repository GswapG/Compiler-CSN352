int main() {
    int result;
    int x = 7;
    switch (x) {
        case 1:
            result = 10;  // Case 1
            break;
        case 2:
            result = 20;  // Case 2 - before break
            break;
            result = 21;  // Unreachable code
        case 3:
            result = 30;  // Case 3 - before fallthrough
            // No break, will fall through to case 4
        default:
            result = 60;  // Default case
            break;
    }
    int endMarker = 99;  // End of switch block marker
}