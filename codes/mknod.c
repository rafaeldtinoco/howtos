#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <attr/xattr.h>

//int mknod(const char *pathname, mode_t mode, dev_t dev);

#define FILENAME "nula"

int
main(int argc, char **argv)
{
	int filed = 0, sockfd = 0;
	struct sockaddr_un sun;

	unlink(FILENAME);

	if ((sockfd = socket(AF_UNIX, SOCK_STREAM, 0)) < 0) {
		fprintf(stderr, "could not create socket\n");
		goto cleanup;
	}

	memset(&sun, 0, sizeof(struct sockaddr_un));
	sun.sun_family = AF_UNIX;
	strncpy(sun.sun_path, FILENAME, sizeof(sun.sun_path) - 1);

	if (bind(sockfd, (const struct sockaddr *) &sun,
	                sizeof(struct sockaddr_un)) < 0) {
		fprintf(stderr, "could not bind socket\n");
		goto cleanup;
	}

	if (fsetxattr(sockfd, "user.testkey", "this is a test value", 20,
	                XATTR_CREATE) < 0) {
		fprintf(stderr, "could not fsetxattr\n");
		perror("fsetxattr");
		goto cleanup;
	}

//	dev_t nula = makedev(1,3);

//	 if(mknod(FILENAME, S_IFCHR | 0777, nula) != 0) {
//	 	fprintf(stderr, "could not mknod\n");
//	 	perror("mknod");
//	 	exit(1);
//	 }
//
//	 if(mknod(FILENAME, S_IFBLK | 0777, nula) != 0) {
//	 	fprintf(stderr, "could not mknod\n");
//	 	perror("mknod");
//	 	exit(1);
//	 }
//
//	 if(mknod("./nula.sock", S_IFSOCK | 0777, nula) != 0) {
//	 	fprintf(stderr, "could not mknod\n");
//	 	perror("mknod");
//	 	exit(1);
//	 }

//	filed = open(FILENAME, O_RDONLY, NULL);
//
//	if (filed < 0) {
//		fprintf(stderr, "could not open file: %d\n", errno);
//		perror("open");
//		exit(1);
//	}
//
//	if (filed > 0)
//		close(filed);

cleanup:

	if (sockfd > 0)
		close(sockfd);

	exit(0);
}
