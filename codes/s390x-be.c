#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <endian.h>

//typedef uint64_t uptr;
//typedef uint64_t ulong;
//typedef uint32_t uint;
//typedef uint8_t uchar;

typedef unsigned char uchar;
typedef unsigned int uint;
typedef unsigned long ulong;

union un {
	uint8_t  u8;
	uint16_t u16;
	uint16_t u32;
	uint16_t u64;
};


int
main(int argc, char *argv)
{
	ulong a, *b;
	ulong *c, d;

	uchar *ptr;
	ulong res;

	union un u = { .u64 = 0x7b };

	a = d = 0;
	b = c =  NULL;

	/* stack */
	a = 0x1000;
	b = &a;

	/* heap */
	c = malloc(sizeof(ulong));
	d = (ulong) (ulong *) c;
	*c = 0x2000;

	printf("ptr to stck addr: 0x%lx and ptr to stck: 0x%lx\n", (ulong)  b, (ulong) *b);
	printf("ptr to stck addr: 0x%lx and ptr to stck: 0x%lx\n", (ulong) &a, (ulong) a );
	printf("ptr to heap addr: 0x%lx and ptr to heap: 0x%lx\n", (ulong)  c, (ulong) *c);
	printf("ptr to heap addr: 0x%lx\n", (ulong)  d);

	/*
	 * example:
	 *
	 * big endian 32-bit integer (4 bytes)
	 *
	 * 0xAA 0xBB 0xCC 0xDD      - in-memory arrangement
	 *
	 * little endian 32-bit integer (4 bytes)
	 *
	 * 0xDD 0xCC 0xBB 0xAA      - in-memory arrangement
	 *
	 */

	a = 0xaabbccdd22334455;

	/*
	 * big endian:
	 *
	 * most significant BYTE (MSB) = 0x55 , least significant BYTE (LSB) = 0xaa
	 *
	 * little endian:
	 *
	 * most significant BYTE (MSB) = 0xaa , least significant BYTE (LSB) = 0x55
	 *
	 * note:
	 *
	 * type convertions start at LEAST SIGNIFICANT BYTE.. explaining:
	 *
	 */

	printf("working with: 0x%lx\n", (ulong) a);

	printf("---\n");

	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[0]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[1]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[2]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[3]));

	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[4]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[5]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[6]));
	printf("testing: 0x%x\n", (uint) (((uchar *) &a)[7]));

	printf("---\n");

	ptr = (char *) &a;

	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+0)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+1)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+2)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+3)));

	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+4)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+5)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+6)));
	printf("testing: 0x%x\n", (uint) ((uchar) *(ptr+7)));

	printf("---\n");

	printf("0x%x\n", (uint) u.u8);
	printf("0x%x\n", (uint) u.u16);
	printf("0x%x\n", (uint) u.u32);
	printf("0x%x\n", (uint) u.u64);
}

