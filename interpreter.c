#include <stdio.h>
#include <string.h>

void parse(char line[]);

FILE *fptr;
char filename[50];

int main(int argc, char *argv[]) {
    
    if (argc > 1) {
        strcpy(filename, argv[1]);
    }
    else {;
        printf("Enter path to file: ");
        scanf("%s", filename);
    }

    fptr = fopen(filename, "r");
    char line[500];

    while(fgets(line, 100, fptr)) {
        parse(line);
    }
    fclose(fptr);
    return 0;
}

void parse(char line[]) {
    printf("%s", line);
}