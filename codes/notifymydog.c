#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <syslog.h>
#include <time.h>
#include <unistd.h>
#include <sys/inotify.h>

#ifndef _DEBUG
#define _DEBUG 0
#endif

#ifndef _SYSLOG
#define _SYSLOG 0
#endif

#define _DBMSG(args...) if(_DEBUG) { fprintf(stdout, args); fprintf(stdout, "\n"); }
#define _DBMSG2(args...) fprintf(stdout, args); fprintf(stdout, "\n");

#define _INMSG(args...) \
        if(_SYSLOG) { \
            syslog(LOG_NOTICE, args); \
        } else { \
            fprintf(stdout, args); \
            fprintf(stdout, "\n"); \
        }

#define _EVESIZE (sizeof(struct inotify_event))
#define _BUFSIZE (1024 * (_EVESIZE + 16))

int
main(int argc, char **argv)
{
	int timesout = 0;
	int ind = 0, inwd = 0, bytes = 0;

	char *inptr, inbuf[_BUFSIZE];

	ind = inotify_init();

	if (ind < 0) {
		fprintf(stderr, "could not initialize inotify\n");
		perror("inotify_init");
		exit(1);
	}

	setlogmask (LOG_UPTO (LOG_NOTICE));
	openlog ("WATCHMYDOG", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);

	inwd = inotify_add_watch(ind, "/dev/watchdog",
	                         IN_ACCESS | IN_ATTRIB | IN_CLOSE_WRITE | IN_CLOSE_NOWRITE |
	                         IN_CREATE | IN_DELETE | IN_DELETE_SELF | IN_MODIFY |
	                         IN_MOVE_SELF | IN_MOVED_FROM | IN_MOVED_TO | IN_OPEN);

	if (inwd < 0) {
		fprintf(stderr, "could not get watch descriptor\n");
		perror("inotify_add_watch");
		exit(1);
	}

	for(;;) {
		memset(&inbuf, 0, _BUFSIZE);
		inptr = (char *) &inbuf;

		bytes = read(ind, inptr, _BUFSIZE);

		if(bytes < 0) {
			fprintf(stderr, "could not read inotify file descriptor\n");
			perror("read");
			goto finish;
		}

		while (bytes) {
			int timesin = 0;

			struct inotify_event *event = (struct inotify_event *) inptr;

			_DBMSG("BUFFER START: %d", bytes)

			if (event->len)
				_DBMSG("LEN: %d", event->len);

			if ((event->mask & IN_OPEN) || (event->mask & IN_ACCESS)) {
				_DBMSG("IN_OPEN or IN_ACCESS")
				_INMSG("WARNING: WATCHDOG WAS OPENED")
			}

			if (event->mask & IN_MODIFY) {
				_DBMSG("IN_MODIFY")

				if (timesout > 100 || timesout == 0) {
					_INMSG("OK: WATCHDOG UPDATED")
					timesout = 0;
				}

				timesout++;
			}

			if ((event->mask & IN_CLOSE_WRITE) || (event->mask & IN_CLOSE_NOWRITE)) {
				_DBMSG("IN_CLOSE_WRITE or IN_CLOSE_NOWRITE")
				_INMSG("WARNING: WATCHDOG WAS CLOSED")
			}

			inptr += (_EVESIZE + event->len);
			bytes -= (_EVESIZE + event->len);

			_DBMSG("BUFFER RESIZE: %d", bytes)
			_DBMSG("EVENTS INSIDE: %d", timesin)
		}
	}

finish:

	if(inotify_rm_watch(ind, inwd) < 0) {
		fprintf(stderr, "could not close watch descriptor\n");
		perror("inotify_rm_watch");
		exit(1);
	}

	if(close(ind) < 0) {
		fprintf(stderr, "could not close inotify\n");
		perror("close");
		exit(1);
	}

	return 0;
}
