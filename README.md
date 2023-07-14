RISC-V interpreter in Python

## Example run of the simulator
```shell
Run this command first: python3 main.py add1-5.obj
Enter the cli interface:
g - go
t - single step
d ads n - dump memory
dis ads n - disassemble content in the memory
r - show registers
s [xn,mn,pc] v - set [reg,mem,pc]
h - this help
q - quit

```

## Acknowledgements

This project uses code from [RISC-V interpreter with detailed control sequences - by prabhas chongstitvatana](https://www.cp.eng.chula.ac.th/~prabhas/project/risc-v/RISC_V_with_controls.htm). Thanks to the authors for their work.
The key enhancement I've implemented is a comprehensive refactor of the instruction decoding segment in `load32.py`, utilizing a Python dictionary for greater efficiency and flexibility. This adjustment is specifically designed to seamlessly support the entirety of the RV32 instruction set. For the simulation of further instructions, simply proceed with the addition of the corresponding instruction implementations within the `rv32c.py` file. 
