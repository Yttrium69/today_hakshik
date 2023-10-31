#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
int main() {
pid_t pid;
int status;
int number;
while (1) {
/* Print the menu here. */
printf("\nmenu\n1. ls -al\n2. ps -a\n3. who\n\n[ENTER] ");
int pick;
scanf("%d", &pick);
int status;
pid = fork();
if (pid != 0) {
/* The parent does something here. */
        wait(&status);
}
else {
/* The child does something here. */
        if(pick == 1) execl("/usr/bin/ls", "ls", "-al", (char *)0);
        else if(pick == 2) execl("/usr/bin/ps", "-a", (char *)0);
        else execl("/usr/bin/who", "", (char *)0);
        exit(0);
}
}
return 0;
}