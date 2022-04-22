#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <inttypes.h>
#include <unistd.h>

struct allptrs {

	void *ptr;

	union {
		uint8_t  u8;
		uint16_t u16;
		uint16_t u32;
		uint16_t u64;
	} map;
};

#define ALL         4096                        // 4096 bytes
#define CHUNKSIZE   256                         // 256 bytes
#define NCHUNKS     (ALL/CHUNKSIZE)             // 16 groups
#define PTRS        (ALL/sizeof(void *))        // pointers in total (512)
#define PTRPCHUNK   (CHUNKSIZE/sizeof(void *))  // pointers per chunk (32)
#define PTRSIZE     (sizeof(void *))            // size of a pointer (usually 8)

int
main(int argc, char *argv)
{
	int i, j;
	unsigned long random, l, longarray[PTRS];
	unsigned long *ptr, **longmap;

	srand(time(0));
	//random=rand();
	random = 0;

	for (l=0; l<PTRS; l++)
		longarray[l] = (long) (l + random);

	longmap = malloc(PTRS);

	if (longmap == NULL) {
		perror("malloc");
		exit(1);
	}

	longmap = malloc(NCHUNKS * PTRSIZE);

	if (longmap == NULL) {
		perror("malloc");
		exit(2);
	}

	for (i=0; i<NCHUNKS; i++) {
		*(longmap+i) = malloc(PTRPCHUNK * PTRSIZE);

		if (*(longmap+i) == NULL) {
			perror("malloc");
			exit(3);
		}
	}
}








