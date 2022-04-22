
#ifndef OUTPUT_H_
#define OUTPUT_H_

#include "main.h"

/* external prototypes */

int output_raw(char **);
int output_zperf_compat(char **);

#define OUTBUFSIZE 8192

#define OUTSTART() 					\
	char *ptr;						\
	*string = malloc(OUTBUFSIZE);	\
	memset(*string, 0, OUTBUFSIZE); \
	ptr = *string;

#define OUTSPRINTF(stuff,args...) ptr += sprintf(ptr, stuff, ##args);

#endif /* OUTPUT_H_ */
