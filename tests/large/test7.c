#include <stdio.h>
#include <string.h>

// Standard struct declaration
struct Point {
    int x;
    int y;
};

// typedef’d struct declaration
typedef struct {
    char name[20];
    int age;
} Person;

int main() {
    struct Point p1 = {10, 20};
    Person person;
    strcpy(person.name, "Alice");
    person.age = 30;
    
    // Nested if‑else control flow
    if(person.age > 20) {
        if(person.age < 40) {
            printf("%s is in his/her prime.\n", person.name);
        } else {
            printf("%s is experienced.\n", person.name);
        }
    } else {
        printf("%s is young.\n", person.name);
    }
    
    // Switch case based on p1.x
    switch(p1.x) {
        case 10:
            printf("p1.x is 10\n");
            break;
        default:
            printf("p1.x is not 10\n");
    }
    
    return 0;
}
