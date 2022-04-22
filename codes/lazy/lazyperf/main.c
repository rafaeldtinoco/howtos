
#include "main.h"
#include "extras.h"
#include "int.h"
#include "lpar.h"
#include "output.h"

extern const char *prog;
//extern struct int_sys *root;

int
main(int argc, char **argv)
{
	int sockfd, lsockfd;
	char *output;
	pid_t pid, sid;
	struct sockaddr_in local, remote;
	socklen_t socksize = sizeof (struct sockaddr_in);

	pid = fork();

	if (pid < 0)
		ERR_EXIT_ERRNO("fork error");

	if (pid > 0)
		exit(0);

	sid = setsid();

	if (sid < 0)
		ERR_EXIT_ERRNO("setsid error");

	//close(2), close(1), close(0);

	memset(&local, 0, sizeof (local));
	local.sin_family = AF_INET;
	local.sin_addr.s_addr = htonl(INADDR_ANY);
	local.sin_port = htons(6969);

	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (!sockfd)
		ERR_EXIT_ERRNO("socket error");

	prog = argv[0];

	ex_init();

	int_init();

	lpar_init();

	bind(sockfd, (struct sockaddr *) &local, sizeof (struct sockaddr));

	if (!sockfd)
		ERR_EXIT_ERRNO("bind error");

	listen(sockfd, 1);

	lsockfd = accept(sockfd, (struct sockaddr *) &remote, &socksize);

	if (!lsockfd)
		ERR_EXIT_ERRNO("accept error");

	while (lsockfd) {
		lpar_update();
		//output_raw(&output);
		output_zperf_compat(&output);
		write(lsockfd, output, strlen(output));
		close(lsockfd);
		lsockfd = accept(sockfd, (struct sockaddr *) &remote, &socksize);

		if (!lsockfd)
			ERR_EXIT_ERRNO("accept error");
	}

	close(lsockfd);
	close(sockfd);

	return 0;
}
