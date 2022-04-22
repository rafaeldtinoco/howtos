
#ifndef INT_H_
#define INT_H_

#include "main.h"
#include "list.h"
#include "extras.h"
#include "lpar.h"

/*
struct int_cputype
{
	char id[INT_CPUTYPE_ID_LEN];
	char desc[INT_CPUTYPE_DESC_LEN];
	u32 idx;
	int cpu_cnt;
};
*/

struct int_cpustats {
	u64 cpu_time_us;
	u64 mgm_time_us;
	u64 wait_time_us;
	s64 steal_time_us;
	u64 online_time_us;
	u64 cpu_corr_us;
	u64 mgm_corr_us;
};

/* cpu possible states */

//enum int_cpustate
//{
//	CPU_STATE_UNKNOWN = 0,
//	CPU_STATE_OPERATING = 1,
//	CPU_STATE_STOPPED = 2,
//	CPU_STATE_DECONFIG = 3,
//};

/* internal cpu abstraction */

struct int_cpu {
	//enum int_cpustate state;
	//char rtype[INT_CPUTYPE_ID_LEN];
	//struct int_cputype *type;

	struct int_sys *parent;

	//u16 cnt;
	u8 active;
	u8 dedicated;
	char id[9];

	struct int_cpustats slot1;
	struct int_cpustats slot2;
	struct int_cpustats *current;
	struct int_cpustats *previous;
	/*
	struct int_os_cpustats os_slot1;
	struct int_os_cpustats os_slot2;
	struct int_os_cpustats *os_current;
	struct int_os_cpustats *os_previous;
	*/

	struct list brothers;
};

/* internal memory abstraction */

struct int_mem {
	u64 min_kib;
	u64 max_kib;
	u64 use_kib;
};

/* internal weight abstraction */

struct int_weight {
	u16 cur;
	u16 min;
	u16 max;
};

/* internal system (cec, lpar or zvm) abstraction */

struct int_sys {
	struct int_sys *parent;
	u8 active;
	u8 dedicated;

	u32 ncpu;
	u32 ncpua;
	u32 nchild;
	u32 nchilda;
	u64 updtime;
	u64 oupdtime;
	u64 corrtime;
	u64 ocorrtime;

	char name[INT_SYSID_SIZE];
	char id[INT_SYSID_SIZE];

	//struct int_mem mem;
	//struct int_weight weight;

	struct list cpus;
	struct list childs;
	struct list brothers;
};

/*
 *
 * global prototypes
 *
 */

void int_init(void);
void int_start(void);
void int_update_sys_start(struct int_sys *);
void int_update_sys_end(struct int_sys *);

struct int_sys *int_get_sys(struct int_sys *, char *);
struct int_sys *int_new_sys(struct int_sys *, char *);
void int_commit_sys(struct int_sys *, u64);

struct int_cpu *int_new_cpu(struct int_sys *, char *);
struct int_cpu *int_get_cpu(struct int_sys *, char *);
void int_is_cpu_ded(struct int_cpu *, int);
void int_commit_cpu(struct int_cpu *);

/* set internal data */

void us_cpu_set(struct int_cpu *, u64);
void us_mgm_set(struct int_cpu *, u64);
void us_online_set(struct int_cpu *, u64);

/* display internal data */

inline u64 dis_tod(struct int_sys *);
inline u64 dis_tod_old(struct int_sys *);
inline u64 dis_tod_delta(struct int_sys *);

inline u64 dis_cpu_cur(struct int_cpu *);
inline u64 dis_cpu_cur_sum(struct int_sys *);
inline u64 dis_cpu_prev(struct int_cpu *);
inline u64 dis_cpu_prev_sum(struct int_sys *);
inline u64 dis_cpu_delta(struct int_cpu *);
inline u64 dis_cpu_delta_sum(struct int_sys *);
inline float dis_cpu_ratio(struct int_cpu *);
inline float dis_cpu_ratio_sum(struct int_sys *);
inline float dis_cpu_util(struct int_cpu *);
inline float dis_cpu_util_sum(struct int_sys *);

inline u64 dis_mgm_cur(struct int_cpu *);
inline u64 dis_mgm_cur_sum(struct int_sys *);
inline u64 dis_mgm_prev(struct int_cpu *);
inline u64 dis_mgm_prev_sum(struct int_sys *);
inline u64 dis_mgm_delta(struct int_cpu *);
inline u64 dis_total_delta_sum(struct int_sys *);
inline float dis_mgm_ratio(struct int_cpu *);
inline float dis_mgm_ratio_sum(struct int_sys *);
inline float dis_mgm_util(struct int_cpu *);
inline float dis_mgm_util_sum(struct int_sys *);

inline u64 dis_total_cur(struct int_cpu *);
inline u64 dis_total_cur_sum(struct int_sys *);
inline u64 dis_total_prev(struct int_cpu *);
inline u64 dis_total_prev_sum(struct int_sys *);
inline u64 dis_total_delta(struct int_cpu *);
inline u64 dis_total_delta_sum(struct int_sys *);
inline float dis_total_ratio(struct int_cpu *);
inline float dis_total_ratio_sum(struct int_sys *);
inline float dis_total_util(struct int_cpu *);
inline float dis_total_util_sum(struct int_sys *);


#endif /* INT_H_ */
