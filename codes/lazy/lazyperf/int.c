
#include "int.h"

/* local prototypes */

void int_start(void);
void int_update_cpu_start(struct int_cpu *);
void int_update_cpu_end(struct int_sys *);

struct int_sys *root;

/* create the cec int_sys structure */

void
int_init(void)
{
	root = int_new_sys(NULL, "ROOT");
	root->parent = NULL;
}

/* create a new int_sys structure (cec, lpar or vm) */

struct int_sys *int_new_sys(struct int_sys *parent, char *id)
{
	struct int_sys *new;

	new = ex_zalloc(sizeof(*new));
	strncpy(new->id, id, sizeof(new->id));

	list_init(&new->childs);
	list_init(&new->cpus);
	list_init(&new->brothers);

	if (parent) {
		new->parent = parent;
		parent->nchild++;
		list_add_end(&new->brothers, &parent->childs);
	}

	return new;
}

struct int_sys *int_get_sys(struct int_sys *parent, char *id)
{
	struct int_sys *sys;

	list_iterate(sys, &parent->childs, brothers)

	if (strcmp(sys->id, id) == 0)
		return sys;

	return NULL ;
}

void
int_commit_sys(struct int_sys *sys, u64 updtime)
{
	struct int_sys *parent = sys->parent;

	sys->active = 1;
	//sys->ocorrtime = sys->corrtime;
	//sys->corrtime = get_tod();
	sys->oupdtime = sys->updtime;
	sys->updtime = updtime;

	if (parent)
		parent->nchilda++;
}

struct int_cpu *int_new_cpu(struct int_sys *parent, char *id)
{
	struct int_cpu *cpu;

	cpu = ex_zalloc(sizeof(*cpu));
	cpu->parent = parent;
	strncpy(cpu->id, id, sizeof(cpu->id));
	cpu->current = &cpu->slot1;
	list_add_end(&cpu->brothers, &parent->cpus);

	return cpu;
}

struct int_cpu *int_get_cpu(struct int_sys *sys, char *id)
{
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)

	if (strcmp(cpu->id, id) == 0)
		return cpu;

	return NULL ;
}

void
int_is_cpu_ded(struct int_cpu *cpu, int weight)
{
	struct int_sys *parent = cpu->parent;

	if(parent)
		if(weight == LPAR_DEDICATED_WEIGHT) {
			if(parent)
				parent->dedicated = 1;

			cpu->dedicated = 1;
		}
}

void
int_commit_cpu(struct int_cpu *cpu)
{
	struct int_sys *parent = cpu->parent;

	cpu->active = 1;

	if (parent)
		parent->ncpua++;
}

void
int_start(void)
{
	struct timespec ts = { 0, INIT_INTERVAL_MS * 1000000 };
	// taking around 3 seconds to start (on purpose)
	lpar_update(); // create structures
	nanosleep(&ts, NULL);
	lpar_update(); // update stats
	//usleep(5*(1000 * 1000));
	//lpar_update(); // update stats (close numbers)
	// service started
}

void
int_update_sys_start(struct int_sys *sys)
{
	struct int_sys *child;
	struct int_cpu *cpu;

	//printf("LPAR: %s, ncpu %d -> %d ncpua\n", sys->id, sys->ncpu, sys->ncpua);
	sys->ncpu = sys->ncpua;
	sys->active = 0;
	sys->nchilda = 0;
	sys->ncpua = 0;

	list_iterate(cpu, &sys->cpus, brothers)
	int_update_cpu_start(cpu);

	list_iterate(child, &sys->childs, brothers)
	int_update_sys_start(child);
}


void
int_update_cpu_start(struct int_cpu *cpu)
{
	struct int_cpustats *tmp;

	cpu->active = 0;

	if (!cpu->previous)
		cpu->previous = &cpu->slot1,
		     cpu->current = &cpu->slot2;
	else
		tmp = cpu->previous,
		cpu->previous = cpu->current,
		     cpu->current = tmp;
}

void
int_update_sys_end(struct int_sys *sys)
{
	struct int_sys *child, *tmp;

	if (sys->nchilda == sys->nchild)
		return;

	int_update_cpu_end(sys);

	list_iterate_safe(child, &sys->childs, brothers, tmp) {
		if (!child->active) {
			list_del(&child->brothers);
			ex_free(child);
			continue;
		}

		int_update_sys_end(child);
	}

	sys->nchild = sys->nchilda;
}

void
int_update_cpu_end(struct int_sys *sys)
{
	struct int_cpu *cpu, *tmp;

	//printf("lpar: %s ncpu: %d, ncpua %d\n", sys->id, sys->ncpu, sys->ncpua);

	if (sys->ncpua == sys->ncpu)
		return;

	list_iterate_safe(cpu, &sys->cpus, brothers, tmp) {
		if (!cpu->active) {
			list_del(&cpu->brothers);
			ex_free(cpu);
			continue;
		}
	}
}

/*
 *
 * FUNCTIONS TO CONFIGURE INTERNAL STRUCTURES
 *
 */

void
us_cpu_set(struct int_cpu *cpu, u64 value)
{
	cpu->current->cpu_time_us = value;
}
void
us_mgm_set(struct int_cpu *cpu, u64 value)
{
	cpu->current->mgm_time_us = value;
}
void
us_online_set(struct int_cpu *cpu, u64 value)
{
	cpu->current->online_time_us = value;
}

/*
 *
 * FUNCTIONS TO DISPLAY INTERNAL STRUCTURES
 * ========================================
 * TODO: all these functions can be converted into a function pointer array
 * so they don't have to be so similar and there is no need to exist so
 * many similar functions.
 *
 */

/*
 * DISPLAY TIME OF THE DAY
 */

inline u64
dis_tod(struct int_sys *sys)
{
	if(sys->dedicated)
		return sys->corrtime;

	return sys->updtime;
};

inline u64
dis_tod_old(struct int_sys *sys)
{
	if(sys->dedicated)
		return sys->ocorrtime;

	return sys->oupdtime;
};

inline u64
dis_tod_delta(struct int_sys *sys)
{
	return (dis_tod(sys) - dis_tod_old(sys));
};

/*
 * DISPLAY CPU CONSUMPTION
 */

inline u64
dis_cpu_cur(struct int_cpu *cpu)
{
	if(cpu->parent->dedicated)
		return cpu->current->cpu_corr_us;

	return cpu->current->cpu_time_us;
}

inline u64
dis_cpu_cur_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_cpu_cur(cpu);

	return sum;
}

inline u64
dis_cpu_prev(struct int_cpu *cpu)
{
	if(cpu->parent->dedicated)
		return cpu->previous->cpu_corr_us;

	return cpu->previous->cpu_time_us;
}

inline u64
dis_cpu_prev_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_cpu_prev(cpu);

	return sum;
}

inline u64
dis_cpu_delta(struct int_cpu *cpu)
{
	return (dis_cpu_cur(cpu) - dis_cpu_prev(cpu));
}

inline u64
dis_cpu_delta_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_cpu_delta(cpu);

	return sum;
}

inline float
dis_cpu_ratio(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_cpu_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res / (u32) cpu->parent->ncpua;
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_cpu_ratio_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_cpu_ratio(cpu);

	return sum;
}

inline float
dis_cpu_util(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_cpu_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_cpu_util_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_cpu_util(cpu);

	return sum;
}

/*
 * DISPLAY MANAGEMENT CONSUMPTION
 */

inline u64
dis_mgm_cur(struct int_cpu *cpu)
{
	if(cpu->parent->dedicated)
		return cpu->current->mgm_corr_us;

	return cpu->current->mgm_time_us;
}

inline u64
dis_mgm_cur_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_mgm_cur(cpu);

	return sum;
}

inline u64
dis_mgm_prev(struct int_cpu *cpu)
{
	if(cpu->parent->dedicated)
		return cpu->previous->mgm_corr_us;

	return cpu->previous->mgm_time_us;
}

inline u64
dis_mgm_prev_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_mgm_prev(cpu);

	return sum;
}

inline u64
dis_mgm_delta(struct int_cpu *cpu)
{
	return (dis_mgm_cur(cpu) - dis_mgm_prev(cpu));
}

inline u64
dis_mgm_delta_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_mgm_delta(cpu);

	return sum;
}

inline float
dis_mgm_ratio(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_mgm_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res / (u32) cpu->parent->ncpua;
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_mgm_ratio_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_mgm_ratio(cpu);

	return sum;
}

inline float
dis_mgm_util(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_mgm_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_mgm_util_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_mgm_util(cpu);

	return sum;
}
/*
 * DISPLAY TOTAL CONSUMPTION
 */

inline u64
dis_total_cur(struct int_cpu *cpu)
{
	return (dis_cpu_cur(cpu) + dis_mgm_cur(cpu));
}

inline u64
dis_total_cur_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_total_cur(cpu);

	return sum;
}

inline u64
dis_total_prev(struct int_cpu *cpu)
{
	return (dis_cpu_prev(cpu) + dis_mgm_prev(cpu));
}

inline u64
dis_total_prev_sum(struct int_sys *sys)
{
	u64 sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_total_prev(cpu);

	return sum;
}

inline u64
dis_total_delta(struct int_cpu *cpu)
{
	return (dis_total_cur(cpu) - dis_total_prev(cpu));
}

inline u64
dis_total_delta_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_total_delta(cpu);

	return sum;
}

inline float
dis_total_ratio(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_total_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res / (u32) cpu->parent->ncpua;
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_total_ratio_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_total_ratio(cpu);

	return sum;
}

inline float
dis_total_util(struct int_cpu *cpu)
{
	float res;

	res = (float) (u64) dis_total_delta(cpu) / (u64) dis_tod_delta(cpu->parent);
	res = (float) (float) res * (int) 100;

	return res;
}

inline float
dis_total_util_sum(struct int_sys *sys)
{
	float sum = 0;
	struct int_cpu *cpu;

	list_iterate(cpu, &sys->cpus, brothers)
	sum += dis_total_util(cpu);

	return sum;
}
