
#include "extras.h"

#include <iconv.h>
#include <mntent.h>
#include <math.h>

static iconv_t localv;

/* init iconv subsystem */

void
ex_init(void)
{
	localv = iconv_open("ISO-8859-1", "EBCDIC-US");

	if (localv == (iconv_t) -1)
		ERR_EXIT("Could not initilize iconv\n");
}

/* MEMORY FUNCTIONS ------------------------------------------------ */

/* alloc "size" memory and return ptr */

void *
ex_alloc(size_t size)
{
	void *ptr = malloc(size);

	if (!ptr)
		ERR_EXIT("Out of memory (%zu Kb)", size / 1024);

	return ptr;
}

/* alloc "size" memory, zero it and return ptr */

void *
ex_zalloc(size_t size)
{
	void *ptr = calloc(1, size);

	if (!ptr)
		ERR_EXIT("Out of memory (%zu Kb)", size / 1024);

	return ptr;
}

/* free memory pointed by ptr */

void
ex_free(void *ptr)
{
	free(ptr);
}

/* CONVERT FUNCTIONS ------------------------------------------------ */

/* convert tod to microsecs */

u64
ex_tod2us(void *ext)
{
	char *tod = ext;
	u64 us, *tod1, *tod2;

	tod1 = (u64 *) tod;
	tod2 = (u64 *) &tod[8];

	us = *tod1 << 8;
	us |= *tod2 >> 58;
	us = us >> 12;

	return us;
}

/* convert ebcdic to ascii */

void
ex_eb2as(char *string, size_t len)
{
	iconv(localv, &string, &len, &string, &len);
}

/* STRING FUNCTIONS ------------------------------------------------ */

/* alloc new memory, copy pointed data and return new ptr */

char *
ex_strdup(char *str)
{
	char *res = ex_alloc(strlen(str) + 1);
	strcpy(res, str);
	return res;
}

/* remove extra white chars from pointer */

char *
ex_strstrip(char *s)
{
	size_t size;
	char *end;

	size = strlen(s);

	if (!size)
		return s;

	end = s + size - 1;

	while (end >= s && isspace(*end))
		end--;

	*(end + 1) = '\0';

	while (*s && isspace(*s))
		s++;

	return s;
}

/* DEBUGFS FUNCTIONS ------------------------------------------------ */

/* get first fs with "type" from mounted dirs */

char *
ex_mntget(char *type)
{
	struct mntent *mntbuf;
	FILE *mounts;

	mounts = setmntent(_PATH_MOUNTED, "r");

	if (!mounts)
		ERR_NULL("could not find \"%s\" mount point", type);

	while ((mntbuf = getmntent(mounts)) != NULL )
		if (strcmp(mntbuf->mnt_type, type) == 0)
			return ex_strdup(mntbuf->mnt_dir);

	endmntent(mounts);

	return NULL ;
}
