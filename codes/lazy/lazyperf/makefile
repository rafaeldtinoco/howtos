# makefile start

CC = gcc

INCLUDES = -Iinclude
CFLAGS = -Wall -g -O3
LFLAGS = -L/lib -L/usr/lib
LIBS = -lm

SRCS = extras.c int.c list.c lpar.c main.c network.c output.c

OBJS = $(SRCS:.c=.o)

MAIN = lazyperf

.PHONY: depend clean

all:		$(MAIN)
		@echo  lazyperf is ready to rock!

$(MAIN):	$(OBJS) 
		$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

.c.o:
		$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
		$(RM) *.o *~ $(MAIN)

depend: $(SRCS)
		makedepend $(INCLUDES) $^

# end
