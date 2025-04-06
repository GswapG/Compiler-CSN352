#include <stdio.h>

struct Person {
    char name[20];
    int age;
};

int main() {
    struct Person person;
    // strcpy(person.name, "Bob");
    person.age = 25;
    printf("%s%d", person.name, person.age);
    return 0;
}
