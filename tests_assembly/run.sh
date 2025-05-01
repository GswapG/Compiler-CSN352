nasm -f elf64 main.asm -o main.o
ld -dynamic-linker /lib64/ld-linux-x86-64.so.2    -lc    /usr/lib/x86_64-linux-gnu/crt1.o    /usr/lib/x86_64-linux-gnu/crti.o    main.o    /usr/lib/x86_64-linux-gnu/crtn.o    -o hello
./hello