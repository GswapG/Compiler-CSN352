int main() {
    int result;
    int x = 7;
    switch (x) {
        case 1:
            result = 10;  // Case 1

        case 2:
            result = 20;  // Case 2 - before break

            result = 21;  // Unreachable code
        case 3:
            result = 30;  // Case 3 - before fallthrough
            // No break, will fall through to case 4
        case 4:
            result = 40;  // Case 4 - after fallthrough
            result = 41;  // Case 4 - continuing execution

        case 5:
            result = 50;  // Case 5

        default:
            result = 60;  // Default case
    }
    int endMarker = 99;  // End of switch block marker
}