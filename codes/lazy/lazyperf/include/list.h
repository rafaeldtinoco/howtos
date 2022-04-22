
#ifndef LIST_H_
#define LIST_H_

#include "main.h"

struct list {
	struct list *next, *prev;
};

#define list_get(entry, type, member) 											\
		((type *)((char *)(entry)-(unsigned long)(&((type *)0)->member)))

#define list_iterate(i, head, member)											\
		for (i = list_get((head)->next, typeof(*i), member);					\
		&i->member != (head);													\
		i = list_get(i->member.next, typeof(*i), member))

#define list_iterate_safe(i, head, member, n)									\
		for (i = list_get((head)->next, typeof(*i), member),					\
				n = list_get(i->member.next, typeof(*i), member);				\
				&i->member != (head);											\
				i = n,															\
				n = list_get(n->member.next, typeof(*n), member))

/* function prototypes */

inline void list_add(struct list *, struct list *);
inline void list_add_end(struct list *, struct list *);
inline void list_del(struct list *);
inline int list_is_empty(struct list *);
inline void list_init(struct list *);

#endif /* LIST_H_ */
