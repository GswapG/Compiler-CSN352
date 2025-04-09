# CSN-352 Compiler: Assumptions and Specifications

**Group 18**  
**Date:** April 6, 2025

---

## Introduction

This document outlines the key assumptions and specifications implemented in our custom compiler. These design choices reflect the current limitations and supported features of our compiler’s architecture.

---

## Assumptions and Specifications

1. **Struct Array Access:**  
   Arrays inside `struct` types must be accessed using standard pointer semantics.

2. **Multidimensional Arrays:**  
   Multidimensional arrays allocated on the stack are treated as pointers to their base type (`type*`).

3. **Array Size Requirements:**  
   Array sizes must be known at compile time. Dynamic array sizing is not supported.

4. **Pointer Size Assumption:**  
   Pointer sizes are assumed to be 64 bits, in line with modern 64-bit architectures.

5. **Pointer Assignment to Stack Arrays:**  
   Any `type*` (pointer to a type) can be assigned to stack-allocated arrays of that type.

6. **Struct Nesting Limitation:**  
   Nested `struct` definitions are not supported at this stage of the compiler.

7. **Function Parameter Support:**  
   Function calls support array parameters only in the following form:
   ```c
   int fun(int arr[], ...);
   ```