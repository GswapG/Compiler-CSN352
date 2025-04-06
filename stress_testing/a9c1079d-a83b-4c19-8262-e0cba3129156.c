#include <stdio.h>

struct Person {
    char name[20];
    int age;
};

int main() {
    struct Person person;
    // strcpy(person.name, "Bob");
    person.age = 25;
    printf("Person: %s, Age: %d\n", person.name, person.age);
    return 0;
}
