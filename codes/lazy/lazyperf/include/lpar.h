
#ifndef LPAR_H_
#define LPAR_H_

#include "main.h"
#include "extras.h"
#include "int.h"

struct d204hdr {
	u64 len;
	u16 version;
	u8 reserved[54];
} __attribute__ ((packed));

struct d204timehdr {
	u8 npar;
	u8 flags;
	//u8 reserved1[6];
	u8 reserved1[4];
	u16 this;
	u64 curtod1;
	u64 curtod2;
	u8 reserved[40];
} __attribute__ ((packed));

struct d204lparhdr {
	u8 reserved1;
	u8 cpus;
	u8 rcpus;
	u8 reserved2[5];
	char sys_name[LPAR_NAME_LEN];
	u8 reserved3[80];
} __attribute__ ((packed));

struct d204lparcpu {
	u16 cpu_addr;
	u8 reserved1[2];
	u8 ctidx;
	u8 reserved2; // new
	u16 weight; // new
	//u8 reserved2[3];
	u64 acc_time;
	u64 lp_time;
	u8 reserved3[6];
	u8 reserved4[2];
	u64 online_time;
	u8 reserved5[56];
} __attribute__ ((packed));

struct d204phyhdr {
	u8 reserved1[1];
	u8 cpus;
	u8 reserved2[94];
} __attribute__ ((packed));

struct d204phycpu {
	u16 cpu_addr;
	u8 reserved1[2];
	u8 ctidx;
	u8 reserved2[3];
	u64 mgm_time;
	u8 reserved3[80];
} __attribute__ ((packed));

/* global prototypes */

int lpar_init(void);
void lpar_update(void);

#endif
