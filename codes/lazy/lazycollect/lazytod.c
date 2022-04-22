#include <time.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

/* accurate monotonic wall clock (s390) or generic clock (x86) */

// this program's binary path
#define BINARY "/tmp/tod"

typedef long s32;
typedef long long s64;
typedef unsigned long long u64;

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
	s64 tod;
	u64 tod2;
	struct timespec t;

	clock_gettime(CLOCK_MONOTONIC_RAW, &t);
	tod = (s32) t.tv_sec;
	tod *= 1000000000;
	tod += t.tv_nsec;

	return (s64) tod;
}

#endif

int
main(int argc, char **argv)
{
	printf("%llu\n", get_tod());

	return 0;
}