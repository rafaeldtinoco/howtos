# notifymydog
Check if watchdog is being updated and if when it was opened and/or closed.
(Purpose: To debug watchdog usage only)

To compile:

```
gcc -Wall -D_DEBUG=0 -D_SYSLOG=1 notifymydog.c -o notifymydog
```

-D_DEBUG=1 -> lots of unneeded data
-D_SYSLOG=1 -> log to syslog (open/close and each 100 watchdog resets)

Example for STDOUT only:

```
inaddy@inaddygueto:~/notifymydog$ gcc -Wall -D_DEBUG=0 -D_SYSLOG=0 notifymydog.c -o notifymydog
inaddy@inaddygueto:~/notifymydog$ sudo ./notifymydog 
OK: WATCHDOG UPDATED
WARNING: WATCHDOG WAS CLOSED
WARNING: WATCHDOG WAS OPENED
OK: WATCHDOG UPDATED
```

Example for SYSLOG only:

```
inaddy@inaddygueto:~/notifymydog$ gcc -Wall -D_DEBUG=0 -D_SYSLOG=1 notifymydog.c -o notifymydog
inaddy@inaddygueto:~/notifymydog$ sudo ./notifymydog &
inaddy@inaddygueto:~$ sudo tail -f /var/log/syslog
Mar 16 17:36:26 inaddygueto WATCHMYDOG[15766]: OK: WATCHDOG UPDATED
Mar 16 17:36:40 inaddygueto WATCHMYDOG[15766]: OK: WATCHDOG UPDATED
Mar 16 17:36:44 inaddygueto WATCHMYDOG[15766]: WARNING: WATCHDOG WAS CLOSED
Mar 16 17:36:49 inaddygueto WATCHMYDOG[15766]: WARNING: WATCHDOG WAS OPENED
```
