
#ifndef MAIN_H_
#define MAIN_H_

#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <fcntl.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>
#include <fcntl.h>
#include <stddef.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>

typedef unsigned long long u64;
typedef signed long long s64;
typedef unsigned int u32;
typedef signed int s32;
typedef unsigned short int u16;
typedef signed short int s16;
typedef unsigned char u8;
typedef signed char s8;

/*
 * MAINFRAME TIME OF THE DAY (DATE: 1900)
 */

#ifdef __s390x__

static inline u64
get_tod(void)
{
	u64 tod;
	asm volatile ("STCK 0(%0)" :: "a" (&tod):"memory","cc");
	return(tod >> 12);
}

#else

static inline u64
get_tod(void)
{
	return 0;
}

#endif

/*
 * usefull macros for all functions
 */

#define MAX(x, y) ((x) > (y) ? (x) : (y))
#define MIN(x, y) ((x) < (y) ? (x) : (y))
#define G0(x) MAX(0, (s64) (x))
#define JIFF2MICRO(var) (u64) (((double)var / (double)HZ) * ((float)(1000 * 1000)))

/*
 * macros for all functions
 */

//#define SD_SYS_ID_SIZE 9

#define HZ 100
#define TMPSIZE 64
#define INT_SYSID_SIZE 9
#define LPAR_NAME_LEN 8
#define LPAR_DEDICATED_WEIGHT 65535
//#define LPAR_DEDICATED_WEIGHT 50
#define D204_FILE "diag_204"
#define STAT_FILE "/proc/stat"
#define STAT_LINE 8192
#define D204_WAIT 10000
#define LPAR_PHYS_FLG 0x80
#define INIT_INTERVAL_MS 200
#define USER_HZ 100
#define MSEC_PER_SEC 1000
#define USEC_PER_SEC 1000000

//#define SD_CPU_TYPE_STR_CP "CP"
//#define SD_CPU_TYPE_STR_UN "UN"
//#define SD_CPU_TYPE_STR_IFL "IFL"

#define int_sys_iterate(parent, sys) list_iterate(sys, &parent->childs, brothers)
#define int_cpu_iterate(parent, cpuptr) list_iterate(cpu, &parent->childs, brothers)

// global program name
const char *prog;

/*
 * error macros for all functions
 */

#define ERR_MSG(x...)                               	\
		do {                                            \
			fflush(stdout);                             \
			fprintf(stderr, "%s: ", prog);				\
			fprintf(stderr, x);                         \
		} while (0)

#define ERR_NEG(x...)                                   \
		do {                                            \
			fflush(stdout);                             \
			fprintf(stderr, "%s: ", prog);				\
			fprintf(stderr, x);                         \
			return -1;									\
		} while (0)

#define ERR_NULL(c, x...)                               \
		do {                                            \
			fflush(stdout);                             \
			fprintf(stderr, "%s: ", prog);				\
			fprintf(stderr, x);                         \
			return c;									\
		} while (0)

#define ERR_EXIT(x...)                              	\
		do {                                            \
			fflush(stdout);                             \
			fprintf(stderr, "%s: ", prog);       		\
			fprintf(stderr, x);                         \
			exit(1);                                    \
		} while (0)

#define ERR_EXIT_ERRNO(x...)                        	\
		do {                                            \
			fflush(stdout);                             \
			fprintf(stderr, "%s: ", prog);       		\
			fprintf(stderr, x);                         \
			fprintf(stderr, " (%s)", strerror(errno));  \
			fprintf(stderr, "\n");                      \
			exit(1);                                    \
		} while (0)

#endif

