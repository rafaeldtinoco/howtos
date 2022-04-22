

#include "lpar.h"

#include <fcntl.h>
#include <libio.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "extras.h"
#include "int.h"
#include "main.h"

/* local prototypes */

void lpar_this(struct d204timehdr *);

int lpar_open(char *);
void lpar_read(struct d204hdr **, struct d204timehdr **);
void lpar_dedread(void);
void lpar_name(struct d204lparhdr *, char *);

void lpar_root_fill(void);
void *lpar_sys_fill(struct int_sys *, struct d204lparhdr *);
void *lpar_cpu_fill(struct int_cpu *, struct d204lparcpu *);

void lpar_cec_fill(struct d204phyhdr *);
void lpar_cec_cpu_fill(struct d204phycpu *);

char *debugdir;
long d204bufsize;

extern struct int_sys *root;
struct int_sys *thislpar;

int
lpar_init(void)
{
	int fd;

	d204bufsize = sizeof(struct d204hdr);

	debugdir = (char *) ex_mntget("debugfs");

	if (!debugdir)
		ERR_NEG("\"mount none -t debugfs /sys/kernel/debug\"\n");

	fd = lpar_open(D204_FILE);

	if(fd < 0)
		ERR_NEG("could not open d204 file\n");

	close(fd);

	int_start();

	return 0;
}

int
lpar_open(char *file)
{
	int fd;
	char path[PATH_MAX];

	if (!file)
		ERR_NEG("filename is empty\n");

	path[0] = 0;
	strcat(path, debugdir);
	strcat(path, "/s390_hypfs/");
	strcat(path, file);

	fd = open(path, O_RDONLY);

	return fd;
}

void
lpar_update(void)
{
	int_update_sys_start(root);
	lpar_root_fill();

	if(thislpar->dedicated == 1)
		lpar_dedread();

	int_update_sys_end(root);
}

void
lpar_root_fill(void)
{

	u64 updtime;
	static u64 lparupdtime;

	struct d204hdr *hdr;
	struct d204timehdr *timehdr;
	struct d204lparhdr *lparhdr;

	int i;
	char lparid[10];
	struct int_sys *lpar;
	static int first = 1;

	do {
		//u64 teste;
		lpar_read(&hdr, &timehdr);
		updtime = ex_tod2us(&timehdr->curtod1);

		if (lparupdtime != updtime) { // d204 takes 1 sec to refresh
			lparupdtime = updtime;
			/*
			teste = get_tod();
			printf("update_time %Ld\n", updtime);
			printf("lparupdtime %Ld\n", lparupdtime);
			printf("get_tod %Ld\n", teste);
			*/
			break;
		}

		ex_free(hdr);

		usleep(D204_WAIT); // wait 0,01 sec before retry
	} while (1);

	lparhdr = ((void *) timehdr) + sizeof(struct d204timehdr);

	for (i = 0; i < timehdr->npar; i++) {
		lpar_name(lparhdr, lparid);
		lpar = int_get_sys(root, lparid);

		if (!lpar)
			lpar = int_new_sys(root, lparid);

		lparhdr = lpar_sys_fill(lpar, lparhdr);
		int_commit_sys(lpar, lparupdtime);
	}

	if (first && (timehdr->flags & LPAR_PHYS_FLG)) {
		lpar_cec_fill((void *) lparhdr);
		lpar_this(timehdr);
		first = 0;
	}

	ex_free(hdr);
	int_commit_sys(root, lparupdtime);
}

void
lpar_cec_fill(struct d204phyhdr *phyhdr)
{
	struct d204phycpu *phycpu;
	int i;

	phycpu = (struct d204phycpu *) (phyhdr + 1);

	for (i = 0; i < phyhdr->cpus; i++) {
		lpar_cec_cpu_fill(phycpu);
		phycpu++;
	}
}

void
lpar_cec_cpu_fill(struct d204phycpu *phycpu)
{
	struct int_cpu *cpu;
	char cpuid[TMPSIZE];

	snprintf(cpuid, TMPSIZE, "%i", phycpu->cpu_addr);
	cpu = int_get_cpu(root, cpuid);

	if (!cpu)
		cpu = int_new_cpu(root, cpuid);

	us_mgm_set(cpu, phycpu->mgm_time);
}

void
lpar_this(struct d204timehdr *timehdr)
{
	char id[10];
	struct d204lparhdr *lparhdr;

	lparhdr = ((void *) timehdr) + timehdr->this;

	lpar_name(lparhdr, id);
	thislpar = int_get_sys(root, id);
}

void
lpar_read(struct d204hdr **hdr, struct d204timehdr **timehdr)
{
	int fd;
	void *buf;
	size_t rc;
	long realsize;

	do {
		*hdr = buf = ex_alloc(d204bufsize);

		fd = lpar_open(D204_FILE);

		if(fd == -1)
			ERR_EXIT("could not open d204 file\n");

		rc = read(fd, buf, d204bufsize);

		if(rc == -1)
			ERR_EXIT("could not read d204 file\n");

		close(fd);

		realsize = (*hdr)->len + sizeof(struct d204hdr);

		if (rc == realsize)
			break;

		d204bufsize = realsize;

		ex_free(buf);
	} while (1);

	*timehdr = buf + sizeof(struct d204hdr);
}

void
lpar_dedread()
{
	FILE *fd;
	int icpuid = 0;
	//u64 tod = 0;
	u64 usr = 0, sys = 0, idle = 0, iowait = 0, steal = 0, none = 0;
	char line[STAT_LINE];
	char cpuid[TMPSIZE];
	struct int_cpu *cpu;

	fd = fopen(STAT_FILE, "r");

	if(fd == NULL)
		ERR_EXIT("could not open stat file\n");

	thislpar->ocorrtime = thislpar->corrtime;
	thislpar->corrtime = get_tod();

	while((fgets(line, STAT_LINE, fd)) != NULL) {
		if ((strncmp(line, "cpu ", 4)) && (!strncmp(line, "cpu", 3))) {
			sscanf(line + 3, "%d %llu %llu %llu %llu %llu %llu %llu %llu %llu %llu",
			       &icpuid, &usr, &none, &sys, &idle, &iowait,
			       &none, &none, &steal, &none, &none);

			snprintf(cpuid, TMPSIZE, "%d", icpuid);
			cpu = int_get_cpu(thislpar, cpuid);

			if (!cpu)
				ERR_EXIT("could not update existent cpu");

			// if really dedicated (shares == 65535) uncomment the line above
			// cpu->current->cpu_corr_us = JIFF2MICRO(usr) + JIFF2MICRO(sys) + JIFF2MICRO(idle) + JIFF2MICRO(iowait);
			// if testing (dedicated if shares == 50, ex) use the one above to get reasonable numbers
			cpu->current->cpu_corr_us = JIFF2MICRO(usr) + JIFF2MICRO(sys);
			cpu->current->mgm_corr_us = JIFF2MICRO(steal);
		}
	}

	fclose(fd);
}

void
lpar_name(struct d204lparhdr *lparhdr, char *name)
{
	memcpy(name, lparhdr->sys_name, LPAR_NAME_LEN);
	ex_eb2as(name, LPAR_NAME_LEN);
	name[LPAR_NAME_LEN] = 0;
	ex_strstrip(name);
}

void *
lpar_sys_fill(struct int_sys *sys, struct d204lparhdr *lparhdr)
{
	struct d204lparcpu *lparcpu;
	int i;

	lparcpu = (struct d204lparcpu *) (lparhdr + 1);

	for (i = 0; i < lparhdr->rcpus; i++) {
		char cpuid[10];
		struct int_cpu *cpu;

		sprintf(cpuid, "%i", lparcpu->cpu_addr);
		cpu = int_get_cpu(sys, cpuid);

		if (!cpu)
			cpu = int_new_cpu(sys, cpuid);

		int_is_cpu_ded(cpu, lparcpu->weight);
		lpar_cpu_fill(cpu, lparcpu);

		int_commit_cpu(cpu);
		lparcpu++;
	}

	return lparcpu;
}

void *
lpar_cpu_fill(struct int_cpu *cpu, struct d204lparcpu *lparcpu)
{
	//printf("\t\tCPU TIME: %Ld\n", lparcpu->lp_time);
	//printf("\t\tMGM TIME: %Ld\n", G0(lparcpu->acc_time - lparcpu->lp_time));
	//printf("\t\tONL TIME: %Ld\n", lparcpu->online_time);

	us_cpu_set(cpu, lparcpu->lp_time);
	us_mgm_set(cpu, G0(lparcpu->acc_time - lparcpu->lp_time));
	us_online_set(cpu, lparcpu->online_time);

	return NULL;
}
