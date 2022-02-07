
## RELOCATIONS (OVERVIEW)

There are other better places for you to read about what relocations are and how linkers and loaders do them. I thought I could add some introductory information here, just the enough so you can follow the rest of the document.
Feel free to skip this session if you're already familiarized with these concepts.

---- 

First, a little bit of old theory from [Linkers & Loaders][1] book. The book is very specialized and with big depth into how linkers and loaders are supposed to work, so I'm only quoting some of important concepts from it.

> A **linkable file** - used as input by a link editor or linking loader contains extensive symbol and relocation information needed by the linker along with the object code. The object code is often divided up into many small logical segments that will be treated differently by the linker.

> An **executable file** - capable of being loaded into memory and run as a program - contains object code to permit the file to be mapped into the address space but doesn’t need any symbols (unless it will do runtime dynamic linking) and needs little or no relocation information.

> The **object code** - capable of being loaded into memory as a library along with a program - is a single large segment, or a small set of segments, that reflect the hardware execution environment, most often read-only vs. read-write pages. Depending on the details of a system’s runtime environment, a loadable file may consist solely of object code, or may contain complete symbol and relocation information to permit runtime symbolic linking.

We use **relocation** to refer both to the process of *adjusting program*
addresses to account for non-zero segment origins, and the process of *resolving references* to external symbols, since the two are frequently handled together.

> Relocation entries serve two functions:
> - When a section of code is relocated to a different base address, relocation entries mark the places in the code that must be modified.
> - In a linkable file, there are also relocation entries that mark references to undefined symbols, so the linker knows where to patch in the symbol’s value when the symbol is finally defined.

> ELF files come in three slightly different flavors: relocatable, executable, and shared object. **Relocatable files** are created by compilers and assemblers but need to be processed by the linker before running. **Executable files** have all relocation done and all symbols resolved except perhaps shared library symbols to be resolved at runtime. **Shared objects** are shared libraries, containing both symbol information for the linker and directly runnable code for runtime.

> A typical relocatable executable has about a dozen sections. Many of the section names are meaningful to the linker, which looks for the section types it knows about for specific processing, while either discarding or passing through unmodified sections (depending on flag bits) that it doesn’t know about.

![relocations-overview-image01.png][image-1]

> ELF sections can be:

```text
.text        type PROGBITS with attributes ALLOC + EXECINSTR.
.data        type PROGBITS with attributes ALLOC + WRITE.
.rodata      type PROGBITS with attribute ALLOC (read-only data).
.bss         type NOBITS with attributes ALLOC + WRITE. 
.rel.text    ...
.rel.data    ...
.rel.rodata  type REL or RELA. (relo info for the text or data sections).
.init        ...
.fini        PROGBITS with attributes ALLOC + EXECINSTR. (similar to .text)
.symtab      type SYMTAB (regular linker symbol table)
.dynsym      tyep DYNSYM (dynamic linker symbol table) with ALLOC (loaded at runtime)
.got         Global Offset Table (for dynamic linking)
.plt         Procedure Linkage Table (for dynamic linking)
.debug       symbols for the debugger
.line        mappings from source line #s to object code locations (debugger)
.comment     documentation strings
```

> A linker combines a set of input file into a single output file ready to be loaded at specific address. If when the program is loaded, storage at that address isn’t available, the loader must relocate the loaded program to reflect the actual load address.

> Each relocatable object file contains a relocation table, a list of places in each segment in the file that need to be relocated. The linker reads in the contents of the segment, applies the relocation items, then disposes of the segment, usually by writing it to the output file.

![relocations-overview-image02.png][image-2]

> Content taken from [Shorne's blog entry][2].

In a regular ELF object (containing no program headers, thus not executable) file we usually have the following sections:

* .rela.text - relocation info for .text section
* [.text][3]: compiled program machine code (contains relocation entries, or placeholders, for addresses of variables located in .data and .bss sections).
* [.data][4] - initialized variable values
* [.bss][5] - non-initialized variables (length, since the memory needed for those variables will be allocated during runtime).

And in an ELF Program file, generated by a linker, we usually have the the following sections:

* .text - contains executable program code (no .rela.text)
* [.got][6] - global offset table used to access variables (created during link time, might be populated during runtime).

---- 

**Summarizing the theory**, we can have:

1.**Link time relocations**: place holders are filled when ELF objects are linked to create ELF executables (or libraries).

By using the [BTFHUB example][7] compilation, we can read relocation tables of a compiled object when it hasn't been linked yet:

```text
$ readelf -r ./example.o

Relocation section '.rela.text' at offset 0x1308 contains 164 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000000000e  002500000004 R_X86_64_PLT32    0000000000000000 malloc - 4
00000000001b  003100000004 R_X86_64_PLT32    0000000000000000 time - 4
00000000002f  002600000004 R_X86_64_PLT32    0000000000000000 memset - 4
000000000038  002300000004 R_X86_64_PLT32    0000000000000000 localtime - 4
00000000004e  002e0000000b R_X86_64_32S      0000000000000000 stdout + 0
000000000054  000800000001 R_X86_64_64       0000000000000000 .rodata.str1.1 + 0
000000000063  000800000001 R_X86_64_64       0000000000000000 .rodata.str1.1 + 1e
00000000006d  000800000001 R_X86_64_64       0000000000000000 .rodata.str1.1 + 28
000000000078  001900000004 R_X86_64_PLT32    0000000000000000 fprintf - 4
000000000080  002e0000000b R_X86_64_32S      0000000000000000 stdout + 0
000000000086  000800000001 R_X86_64_64       0000000000000000 .rodata.str1.1 + 35
000000000091  001900000004 R_X86_64_PLT32    0000000000000000 fprintf - 4
000000000099  002e0000000b R_X86_64_32S      0000000000000000 stdout + 0
00000000009e  001700000004 R_X86_64_PLT32    0000000000000000 fflush - 4
...
```

And read the non-stripped symbol table of it, to give a meaning to the last column of the last command.

```text
$ readelf --syms ./example.o

Symbol table '.symtab' contains 54 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
	 0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND
	 1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS example.c
	 2: 0000000000000000    16 OBJECT  LOCAL  DEFAULT    5 .L__const.bump_m[...]
	 3: 0000000000000000     4 OBJECT  LOCAL  DEFAULT    6 bpfverbose
	 4: 0000000000000004     1 OBJECT  LOCAL  DEFAULT    6 exiting
	 5: 0000000000000820   302 FUNC    LOCAL  DEFAULT    2 get_pid_max
	 6: 0000000000000250   153 FUNC    LOCAL  DEFAULT    2 output
	 7: 0000000000000000     0 SECTION LOCAL  DEFAULT    2
	 8: 0000000000000000     0 SECTION LOCAL  DEFAULT    4
	 9: 0000000000000000     0 SECTION LOCAL  DEFAULT    5
	10: 0000000000000000     0 SECTION LOCAL  DEFAULT    6
	11: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND __isoc99_fscanf
	12: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_map__fd
	13: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_object__close
	14: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_object__find[...]
	15: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_object__find[...]
	16: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_object__load
	17: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_object__open_file
	18: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_program__attach
	19: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND bpf_program__set[...]
	20: 0000000000000140    52 FUNC    GLOBAL DEFAULT    2 bump_memlock_rlimit
	21: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND exit
	22: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND fclose
	23: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND fflush
	24: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND fopen
	25: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND fprintf
	26: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND free
...
```

As you can see here, some relocations might be solved during *link time*, like the ones that are related to local symbols (of all objects being linked), and some others can't.

A good example of *link time* relocation is the relocation to find a local (to the object) function address. Let's use the **usage** function of our example. In the relocation table the entry is:

```text
000000000428  003400000004 R_X86_64_PLT32    00000000000001e0 usage - 4

and the symbol usage, in the symbol table, is:

52: 00000000000001e0    54 FUNC    GLOBAL DEFAULT    2 usage
```

I like the way [this document][8] describes interpretation of this. Relocation tables tell ELF linker: "Be careful, what is at offset 428 has to be replaced by an address that can be calculated in the way described by the relocation type `R_X86_64_PLT32`. For such calculation, you can use the value of the symbol whose index resides in the relocation entry (usage) and the addend (here -4).

So, at the end, the relocation is *S + A - P* where:

```text
* S: The value of the symbol whose index resides in the relocation entry.
* A: The addend used to compute the value of the relocatable field.
* P: The section offset or address of the storage unit being relocated
```

2.**Load time relocations**: place holders are filled during runtime by the
   dynamic linker.

*Load time relocations* are meant for 2 purposes: To do relocations when using dynamic libraries AND to allow [Position Independent Code][9]

To show more information about *load time relocations* its better if we work with Linux executables. As all of the Linux binaries were already linked, we can now see the side effects of the *link time relocations* made to them. Look at an existing Linux binary relocation tables:

```text
$ readelf -r /bin/ls

Relocation section '.rela.dyn' at offset 0x17b8 contains 216 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000022fd0  000000000008 R_X86_64_RELATIVE                    68f0
000000022fd8  000000000008 R_X86_64_RELATIVE                    68b0
000000022fe0  000000000008 R_X86_64_RELATIVE                    8620
000000022fe8  000000000008 R_X86_64_RELATIVE                    8c40
000000022ff0  000000000008 R_X86_64_RELATIVE                    8650
000000022ff8  000000000008 R_X86_64_RELATIVE                    8d00
000000023000  000000000008 R_X86_64_RELATIVE                    6fd0
000000023008  000000000008 R_X86_64_RELATIVE                    7000
...

000000023fb8  007000000006 R_X86_64_GLOB_DAT 0000000000000000 free@GLIBC_2.2.5 + 0
000000023fd0  004100000006 R_X86_64_GLOB_DAT 0000000000000000 __gmon_start__ + 0
000000023fd8  007e00000006 R_X86_64_GLOB_DAT 0000000000000000 malloc@GLIBC_2.2.5 + 0
0000000242c0  007600000005 R_X86_64_COPY     00000000000242c0 stderr@GLIBC_2.2.5 + 0
...

Relocation section '.rela.plt' at offset 0x2bf8 contains 105 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000023c78  000200000007 R_X86_64_JUMP_SLO 0000000000000000 getenv@GLIBC_2.2.5 + 0
000000023c80  000300000007 R_X86_64_JUMP_SLO 0000000000000000 fgetfilecon@LIBSELINUX_1.0 + 0
000000023c88  000400000007 R_X86_64_JUMP_SLO 0000000000000000 sigprocmask@GLIBC_2.2.5 + 0
000000023c90  000500000007 R_X86_64_JUMP_SLO 0000000000000000 __snprintf_chk@GLIBC_2.3.4 + 0
000000023c98  000600000007 R_X86_64_JUMP_SLO 0000000000000000 raise@GLIBC_2.2.5 + 0
000000023ca0  000700000007 R_X86_64_JUMP_SLO 0000000000000000 abort@GLIBC_2.2.5 + 0
000000023cb0  000900000007 R_X86_64_JUMP_SLO 0000000000000000 strncmp@GLIBC_2.2.5 + 0
....
```

> (I have stripped some middle lines of the output)

> The reason why you only see a number, and can't see the symbol name, at the end of the relocation table, showed in the previous `readelf` example, is because this binary has been stripped, removing unnecessary (to run) data.

This is an execution file, so it does not contain a `.rela.text` section, used by the linker during *link time*, as seen in the previous item.

```text
$ readelf --wide -S /bin/ls
There are 31 section headers, starting at offset 0x23418:

Section Headers:
...
  [Nr] Name              Type            Address          Off    Size   ES Flg Lk Inf Al
  [ 6] .dynsym           DYNSYM          0000000000000450 000450 000c00 18   A  7   1  8
  [ 7] .dynstr           STRTAB          0000000000001050 001050 0005c5 00   A  0   0  1
...
  [10] .rela.dyn         RELA            00000000000017b8 0017b8 001440 18   A  6   0  8
  [11] .rela.plt         RELA            0000000000002bf8 002bf8 0009d8 18  AI  6  25  8
  [13] .plt              PROGBITS        0000000000004020 004020 0006a0 10  AX  0   0 16
  [14] .plt.got          PROGBITS        00000000000046c0 0046c0 000030 10  AX  0   0 16
  [15] .plt.sec          PROGBITS        00000000000046f0 0046f0 000690 10  AX  0   0 16
...
  [23] .data.rel.ro      PROGBITS        0000000000022fe0 021fe0 000a78 00  WA  0   0 32
  [24] .dynamic          DYNAMIC         0000000000023a58 022a58 000200 10  WA  7   0  8
  [25] .got              PROGBITS        0000000000023c58 022c58 000398 08  WA  0   0  8
  [26] .data             PROGBITS        0000000000024000 023000 000268 00  WA  0   0 32
  [27] .bss              NOBITS          0000000000024280 023268 0012d8 00  WA  0   0 32
```

Instead, all the local (to the object) relocations will now, during the link time phase, be resolved by:

* the `.got` (global offset table) or `.got.plt` (procedure linkage table) sections - to deal with position independence: both sections are loaded on R/W memory pages and are updated according to how the dynamic loader sees fit.

* AND the remaining relocations (to external shared libraries/objects) will be resolved with `.rela.dyn`  and `.rela.plt` sections.

Relocation table entries from those sections will point to symbol tables and have declared a relocation type and the needed addend (if the type needs one).

!!! NOTE
    After *link time relocations* your binary can be either *statically* or *dynamically* executed. If it is a *dynamic* binary, for example, then you will need the **load time relocations** to satisfy position independent code and the shared library symbol (or global variable) addresses, only known at load/execution time

[1]:	https://www.amazon.com/Linkers-Kaufmann-Software-Engineering-Programming/dp/1558604960
[2]:	https://stffrdhrn.github.io/hardware/embedded/openrisc/2019/11/29/relocs.html
[3]:	https://en.wikipedia.org/wiki/Code_segment
[4]:	https://en.wikipedia.org/wiki/Data_segment
[5]:	https://en.wikipedia.org/wiki/.bss
[6]:	https://en.wikipedia.org/wiki/Global_Offset_Table
[7]:	https://github.com/aquasecurity/btfhub/tree/main/example
[8]:	https://stac47.github.io/c/relocation/elf/tutorial/2018/03/01/understanding-relocation-elf.html
[9]:	https://en.wikipedia.org/wiki/Position-independent_code

[image-1]:	images/relocations-overview/image01.png
[image-2]:	images/relocations-overview/image02.png
