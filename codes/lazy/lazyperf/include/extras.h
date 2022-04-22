
#ifndef EXTRAS_H_
#define EXTRAS_H_

#include "main.h"

void ex_init(void);

/* memory funtions */
void *ex_alloc(size_t);
void *ex_zalloc(size_t);
void ex_free(void *);

/* convert functions */
u64 ex_tod2us(void *);
void ex_eb2as(char *, size_t);

/* string functions */
char *ex_strdup(char *);
char *ex_strstrip(char *);

/* debugfs functions*/
char *ex_mntget(char *);

float ull2float(u64);

#endif /* EXTRAS_H_ */
