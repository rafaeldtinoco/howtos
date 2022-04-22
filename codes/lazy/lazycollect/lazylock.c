#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/file.h>

/* this program's binary path */
#define BINARY "/tmp/lock"

#define LOCKFILE "/tmp/.lazylock"
#define CHILDFILE "/tmp/.lazychild"

char *lockfile = LOCKFILE;
char *childfile = CHILDFILE;

int
try_to_lock(int fd)
{
	int i = 0;

	for (i = 0; i < 10; i++) {
		if (flock(fd, LOCK_EX) == 0)
			return 0;

		usleep(200000);
	}

	return -1;
}

int
unlock(int fd)
{
	return flock(fd, LOCK_UN);
}

int
child(int fd, int what)
{
	int nchild = 0;
	char out[100];
	char in[100];

	memset((char *) &in, 0, 100);
	read(fd, (char *) &in, 100);
	nchild = atoi(in);

	if (what == 3)
		return nchild;

	if (what == 2)
		nchild--;

	if (what == 1)
		nchild++;

	lseek(fd, 0, SEEK_SET);
	memset(&out, 0, 100);
	write(fd, out, 100);

	lseek(fd, 0, SEEK_SET);
	sprintf(out, "%d", nchild);
	write(fd, out, 100);

	return nchild;
}

int
main(int argc, char **argv)
{
	int lockfd = 0;
	int childfd = 0;
	char opt;

	if ((lockfd = open(lockfile, O_CREAT | O_SYNC | O_RDWR)) < 0)
		fprintf(stderr, "could not open/create lock file\n"), exit(1);

	if (try_to_lock(lockfd) < 0)
		fprintf(stderr, "could not lock the lockfile\n"), exit(-1);

	if ((childfd = open(childfile, O_CREAT | O_SYNC | O_RDWR)) < 0)
		fprintf(stderr, "could not open/create childfile\n"), exit(1);

	opt = (char) *argv[1];

	if (opt != 'a' && opt != 'r' && opt != 'g')
		fprintf(stderr, "syntax: %s [a|r|g]\n", argv[0]), exit(1);

	if (opt == 'a')
		childnr = child(childfd, 1);
	else if (opt == 'r')
		childnr = child(childfd, 2);
	else if (opt == 'g') {
		childnr = child(childfd, 3);
		printf("%d\n", childnr);
	}

	close(childfd);
	unlock(lockfd);
	close(lockfd);

	return 0;
}
