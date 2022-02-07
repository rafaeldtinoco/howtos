#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define BUFFER "aeiouaeiouaeiouaeiou"
#define TPFILE "/tmp/bleh"

#define fatal(str)\
    {\
        fprintf(stderr, "%s\n", str);\
        fflush(stderr);\
        exit(1);\
    }

#define fatality(str)\
    {\
        perror(str);\
        fflush(stderr);\
        exit(1);\
    }

#define out(str...)\
    {\
        fprintf(stdout, "(%d) ", getpid());\
        fprintf(stdout, str);\
        fflush(stdout);\
    }

int
main(int argc, char *argv[])
{
	int pid, status;
	int ret = 0;
	int fd[2];

	ret = socketpair(AF_UNIX, SOCK_STREAM, 0, fd);

	if (ret != 0)
		fatality("socketpair");

	pid = fork();

	if (pid == 0) {

		// parent

		int filed, status;
		char buffer[21], filebuf[1024];
		struct msghdr msg;
		struct iovec iov;
		struct cmsghdr *cmsg;

		union {
			char buf[CMSG_SPACE(sizeof(int))];
			struct cmsghdr align;
		} cmsgu;

		close(fd[1]);
		memset(&filebuf, 0, 1024);
		memset(&buffer, 0, 21);

		strncpy((char *) &buffer, BUFFER, 21);

		// tmpfile: create contents

		filed = open(TPFILE, O_CREAT | O_TRUNC | O_RDWR, S_IRUSR | S_IWUSR);

		if (filed == -1)
			fatality("open");

		ret = write(filed, "1234567890", 10);

		if (ret != 10)
			fatality("write");

		close(filed);

		// tmpfile: check contents

		filed = open(TPFILE, O_RDONLY);

		if (filed == -1)
			fatality("open");

		ret = read(filed, &filebuf, 1024);

		if (ret < 0)
			fatal("could not read tmpfile");

		close(filed);

		// tmpfile: open fd

		filed = open(TPFILE, O_RDONLY);

		if (filed == -1)
			fatality("open");

		// prepare control message to be sent

		memset(&msg, 0, sizeof(struct msghdr));
		memset(&iov, 0, sizeof(struct iovec));

		iov.iov_base = &buffer;
		iov.iov_len = 21;

		msg.msg_name = NULL;
		msg.msg_namelen = 0;
		msg.msg_iov = &iov;
		msg.msg_iovlen = 1;
		msg.msg_control = cmsgu.buf;
		msg.msg_controllen = sizeof(cmsgu.buf);

		cmsg = CMSG_FIRSTHDR(&msg);
		cmsg->cmsg_level = SOL_SOCKET;
		cmsg->cmsg_type = SCM_RIGHTS;
		cmsg->cmsg_len = CMSG_LEN(sizeof(int));

		memcpy(CMSG_DATA(cmsg), &filed, sizeof(int));

		// send control message

		ret = sendmsg(fd[0], &msg, 0);

		if (ret == -1)
			fatality("sendmsg");

		// finish

		out("buffer sent: %s\n", buffer);
		out("file descriptor: %d\n", filed);
		out("file contents: %s\n", filebuf);

		wait(&status);

		close(filed);
		unlink(TPFILE);

	} else {

		// child

		int childfd;
		char buffer[21], filebuf[1024];
		struct msghdr msg;
		struct iovec iov;
		struct cmsghdr *cmsg;

		union {
			char buf[CMSG_SPACE(sizeof(int))];
			struct cmsghdr align;
		} cmsgu;

		close(fd[0]);

		memset(&filebuf, 0, 1024);
		memset(&buffer, 0, 21);
		memset(&msg, 0, sizeof(struct msghdr));
		memset(&iov, 0, sizeof(struct iovec));

		// prepare control message to be received

		iov.iov_base = &buffer;
		iov.iov_len = 21;

		msg.msg_name = NULL;
		msg.msg_namelen = 0;
		msg.msg_iov = &iov;
		msg.msg_iovlen = 1;
		msg.msg_control = cmsgu.buf;
		msg.msg_controllen = sizeof(cmsgu.buf);

		// receive control message

		ret = recvmsg(fd[1], &msg, 0);

		if (ret == -1)
			fatality("sendmsg");

		cmsg = CMSG_FIRSTHDR(&msg);
		childfd = *(int *) CMSG_DATA(cmsg);

		// finish

		out("buffer received: %s\n", buffer);
		out("file descriptor: %d\n", childfd);

		ret = read(childfd, &filebuf, 1024);

		if (ret == -1)
			fatality("read");

		out("file contents: %s\n", filebuf);
	}

	exit(0);
}
