#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>
int main() {
int status;

printf("Program has been started!\n");

pid_t child = fork();


if(child!=0){ //parent
        int status_child;
        printf("<%d> is parent.\n", getpid());
        sleep(1);
        wait(&status_child);
        if(WIFEXITED(status_child)) printf("<%d> Parent has waited for all the children.\n", getpid());
}
else{
        printf("<%d> is the son.\n", getpid());
        int status_grand_child;
        pid_t grand_child = fork();
        if(grand_child ==0){
                printf("<%d> is the grand-son.\n", getpid());
                printf("<%d> Grand-son exit.\n", getpid());
                exit(0);
        }
        sleep(1);
        wait(&status_grand_child);

        if(WIFEXITED(status_grand_child)){
        printf("<%d> Son exit.\n", getpid());
        exit(0);}
}


}