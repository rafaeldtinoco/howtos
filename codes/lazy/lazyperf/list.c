
#include "list.h"

/* add one entry into a list using its head */

inline void
list_add(struct list *entry, struct list *head)
{
	entry->next = head->next;
	entry->next->prev = entry;
	head->next = entry;
	entry->prev = head;
}

/* add one entry into the end of a list using list's head */

inline void
list_add_end(struct list *entry, struct list *head)
{
	entry->prev = head->prev;
	entry->prev->next = entry;
	head->prev = entry;
	entry->next = head;
}

/* del entry from the list where it is contained */

inline void
list_del(struct list *entry)
{
	entry->next->prev = entry->prev;
	entry->prev->next = entry->next;
	entry->next = entry;
	entry->prev = entry;
}

/* check if the list is empty */

inline int
list_is_empty(struct list *head)
{
	if ((head->next == head) && (head->prev == head))
		return 1;
	else
		return 0;
}

/* initialize one line */

inline void
list_init(struct list *head)
{
	head->next = head;
	head->prev = head;
}

