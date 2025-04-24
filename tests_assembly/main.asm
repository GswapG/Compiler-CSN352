section .data
msg db "Hello 123123", 10 ,0
section .text
global main
extern exit
extern printf
_start:
    and rbp, 0xfffffffffffffff0
    call main

    mov rdi, rax
    call exit
main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rdi, msg
    call printf
    mov rax, 0
    leave
    ret