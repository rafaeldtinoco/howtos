
#include "output.h"
#include "list.h"
#include "int.h"

extern struct int_sys *thislpar;

int
output_raw(char **string)

{

	/*
	 *
	 * this function is responsible to tell developer if every number is
	 * behaving just like it need to. so all the math errors are going
	 * to be seen here.
	 *
	 * i'm only using "thislpar" to show raw data so far.
	 *
	 */

	struct int_cpu *cpu;

	OUTSTART();

	list_iterate(cpu, &thislpar->cpus, brothers)

	{

		OUTSTART();

		OUTSPRINTF("TOD: %12llu\n", dis_tod(thislpar));

		OUTSPRINTF("LPAR: %s CPU: %s\n\n", thislpar->id, cpu->id);


		OUTSPRINTF("\nRAW DATA\n\n");



		OUTSPRINTF("\tcurrent:\n");

		OUTSPRINTF("\t\ttime of day: %llu\n",cpu->parent->updtime);
		OUTSPRINTF("\t\tcputime: %llu\n", cpu->current->cpu_time_us);
		OUTSPRINTF("\t\tmgmtime: %llu\n", cpu->current->mgm_time_us);
		OUTSPRINTF("\t\tonltime: %llu\n", cpu->current->online_time_us);

		OUTSPRINTF("\n\tcurrent guest:\n");
		OUTSPRINTF("\t\ttime of day: %llu\n",cpu->parent->corrtime);
		OUTSPRINTF("\t\tcputime: %llu\n", cpu->current->cpu_corr_us);
		OUTSPRINTF("\t\tmgmtime: %llu\n", cpu->current->mgm_corr_us);

		OUTSPRINTF("\n\tprevious:\n");
		OUTSPRINTF("\t\ttime of day: %llu\n",cpu->parent->oupdtime);
		OUTSPRINTF("\t\tcputime: %llu\n", cpu->previous->cpu_time_us);
		OUTSPRINTF("\t\tmgmtime: %llu\n", cpu->previous->mgm_time_us);
		OUTSPRINTF("\t\tonltime: %llu\n", cpu->previous->online_time_us);

		OUTSPRINTF("\n\tprevious guest:\n");
		OUTSPRINTF("\t\ttime of day: %llu\n",cpu->parent->ocorrtime);
		OUTSPRINTF("\t\tcputime: %llu\n", cpu->previous->cpu_corr_us);
		OUTSPRINTF("\t\tmgmtime: %llu\n\n", cpu->previous->mgm_corr_us);

		OUTSPRINTF("CALCULATIONS\n\n");

		OUTSPRINTF("\tcurrent:\n");
		OUTSPRINTF("\t\ttime of day: %llu\n", dis_tod(cpu->parent));
		OUTSPRINTF("\t\tcputime: %llu\n", dis_cpu_cur(cpu));
		OUTSPRINTF("\t\tmgmtime: %llu\n", dis_mgm_cur(cpu));
		OUTSPRINTF("\t\ttottime: %llu\n\n", dis_total_cur(cpu));

		OUTSPRINTF("\tprevious:\n");
		OUTSPRINTF("\t\ttime of day: %llu\n", dis_tod_old(cpu->parent));
		OUTSPRINTF("\t\tcputime: %llu\n", dis_cpu_prev(cpu));
		OUTSPRINTF("\t\tmgmtime: %llu\n", dis_mgm_prev(cpu));
		OUTSPRINTF("\t\ttottime: %llu\n\n", dis_total_prev(cpu));

		OUTSPRINTF("STATISTICS:\n\n");

		OUTSPRINTF("\ttime of day delta: %llu\n\n", dis_tod_delta(cpu->parent));
		OUTSPRINTF("\t\tcputime delta: %llu\n", dis_cpu_delta(cpu));
		OUTSPRINTF("\t\tcputime ratio: %f\n", dis_cpu_ratio(cpu));
		OUTSPRINTF("\t\tcputime util: %f\n\n", dis_cpu_util(cpu));

		OUTSPRINTF("\t\tmgmtime delta: %llu\n", dis_mgm_delta(cpu));
		OUTSPRINTF("\t\tmgmtime ratio: %f\n", dis_mgm_ratio(cpu));
		OUTSPRINTF("\t\tmgmtime util: %f\n\n", dis_mgm_util(cpu));

		OUTSPRINTF("\t\ttottime delta: %llu\n", dis_total_delta(cpu));
		OUTSPRINTF("\t\ttottime ratio: %f\n", dis_total_ratio(cpu));
		OUTSPRINTF("\t\ttottime util: %f\n\n", dis_total_util(cpu));
	}

	return 0;
}



int
output_zperf_compat(char **string)
{
	struct int_cpu *cpu;

	OUTSTART();

	OUTSPRINTF("TOD: %12llu\n", dis_tod(thislpar));


	OUTSPRINTF("CPU consumption since LPAR activate:\n");
	OUTSPRINTF("\t Image CPU: %llu us \n", dis_cpu_cur_sum(thislpar));
	OUTSPRINTF("\t LPAR CPU:  %llu us \n", dis_mgm_cur_sum(thislpar));
	OUTSPRINTF("\t total CPU: %llu us \n", dis_total_cur_sum(thislpar));

	OUTSPRINTF("\nCPU consumption since last display:\n");
	OUTSPRINTF("\t Image CPU: %llu us\n", dis_cpu_prev_sum(thislpar));
	OUTSPRINTF("\t LPAR CPU:  %llu us\n", dis_mgm_prev_sum(thislpar));
	OUTSPRINTF("\t total CPU: %llu us\n", dis_total_prev_sum(thislpar));
	OUTSPRINTF("\t TOD:       %llu us\n", dis_tod_delta(thislpar));

	OUTSPRINTF("TOD: %12llu 탎 +%llu 탎\n", dis_tod(thislpar), dis_tod_delta(thislpar));
	OUTSPRINTF(" CPUID     IMAGE-탎     TOTAL-탎    +IMAGE-탎  ratio-%% util-%%    +TOTAL-탎  ratio-%% util-%%\n");

	list_iterate(cpu, &thislpar->cpus, brothers)

	{
		OUTSPRINTF("CPU%03d %12llu %12llu %12llu  %6.2f %6.2f %12llu  %6.2f %6.2f\n",
		           atoi(cpu->id),					// cpu id number
		           dis_cpu_cur(cpu),   		    // current cpu utilization
		           dis_total_cur(cpu),				// current total utilization
		           dis_cpu_delta(cpu),				// cpu utilization since last time
		           dis_cpu_ratio(cpu),				// cpu ratio since last time
		           dis_cpu_util(cpu),				// cpu utilization (%) since last time
		           dis_total_delta(cpu),			// total utilization since last time
		           dis_total_ratio(cpu),			// total ratio since last time
		           dis_total_util(cpu)				// total utilization (%) since last time
		          );
	}

	OUTSPRINTF("CPUall %12llu %12llu %12llu      -- %6.2f %12llu      -- %6.2f\n",
	           dis_cpu_cur_sum(thislpar),
	           dis_total_cur_sum(thislpar),
	           dis_cpu_delta_sum(thislpar),
	           // dis_cpu_ratio_sum(thislpar),
	           dis_cpu_util_sum(thislpar),
	           dis_total_delta_sum(thislpar),
	           // dis_total_ratio_sum(thislpar),
	           dis_total_util_sum(thislpar)
	          );

	return 0;
}
