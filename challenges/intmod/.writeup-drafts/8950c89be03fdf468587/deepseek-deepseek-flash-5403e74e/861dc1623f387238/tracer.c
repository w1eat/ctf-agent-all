#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <sys/types.h>
#include <signal.h>

int main(int argc, char **argv){
    pid_t pid = fork();
    if(pid==0){
        ptrace(PTRACE_TRACEME,0,0,0);
        freopen("/tmp/in.bin","rb",stdin);
        execl("./intmod","./intmod",(char*)0);
        _exit(127);
    }
    int status; waitpid(pid,&status,0);
    ptrace(PTRACE_SETOPTIONS,pid,0,0);
    ptrace(PTRACE_CONT,pid,0,0);
    long count=0; FILE *f=fopen("/tmp/ptrace.log","w");
    while(1){
        waitpid(pid,&status,0);
        if(WIFEXITED(status)){ fprintf(f,"EXIT %d\n",WEXITSTATUS(status)); break; }
        if(WIFSIGNALED(status)){ fprintf(f,"KILLED sig %d\n",WTERMSIG(status)); break; }
        struct user_regs_struct r; ptrace(PTRACE_GETREGS,pid,0,&r);
        int sig=WSTOPSIG(status);
        fprintf(f,"%ld RIP=%llx sig=%d r8=%llx r9=%llx r10=%llx r11=%llx r12=%llx r13=%llx r14=%llx rax=%llx rcx=%llx rdx=%llx rsi=%llx rdi=%llx\n",
            count,(unsigned long long)r.rip,sig,r.r8,r.r9,r.r10,r.r11,r.r12,r.r13,r.r14,r.rax,r.rcx,r.rdx,r.rsi,r.rdi);
        count++;
        if(count>30000) { fprintf(f,"LIMIT\n"); break; }
        ptrace(PTRACE_CONT,pid,0,sig);
    }
    fclose(f); return 0;
}
