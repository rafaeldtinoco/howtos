#include <syscall.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

#include <sys/syscall.h>
#include <linux/membarrier.h>

#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))

struct test_case {
	char testname[80];
	int command;            /* membarrier cmd                            */
	int needregister;       /* membarrier cmd needs register cmd         */
	int flags;              /* flags for given membarrier cmd        */
	long exp_ret;           /* expected return code for given cmd        */
	int exp_errno;          /* expected errno for given cmd failure      */
	int enabled;            /* enabled, despite results from CMD_QUERY   */
	int always;             /* CMD_QUERY should always enable this test  */
	int force;              /* force if CMD_QUERY reports not enabled    */
	int force_exp_errno;    /* expected errno after forced cmd           */
};

struct test_case tc[] = {
	{
		/*
		 * case 00) invalid cmd
		 *     - enabled by default
		 *     - should always fail with EINVAL
		 */
		.testname = "cmd_fail",
		.command = -1,
		.exp_ret = -1,
		.exp_errno = EINVAL,
		.enabled = 1,
	},
	{
		/*
		 * case 01) invalid flags
		 *     - enabled by default
		 *     - should always fail with EINVAL
		 */
		.testname = "cmd_flags_fail",
		.command = MEMBARRIER_CMD_QUERY,
		.flags = 1,
		.exp_ret = -1,
		.exp_errno = EINVAL,
		.enabled = 1,
	},
	{
		/*
		 * case 02) global barrier
		 *     - should ALWAYS be enabled by CMD_QUERY
		 *     - should always succeed
		 */
		.testname = "cmd_global_success",
		.command = MEMBARRIER_CMD_GLOBAL,
		.flags = 0,
		.exp_ret = 0,
		.always = 1,
	},
	/*
	 * commit 22e4ebb975 (v4.14-rc1) added cases 03, 04 and 05 features:
	 */
	{
		/*
		 * case 03) private expedited barrier with no registrations
		 *     - should fail with errno=EPERM due to no registrations
		 *     - or be skipped if unsupported by running kernel
		 */
		.testname = "cmd_private_expedited_fail",
		.command = MEMBARRIER_CMD_PRIVATE_EXPEDITED,
		.flags = 0,
		.exp_ret = -1,
		.exp_errno = EPERM,
	},
	{
		/*
		 * case 04) register private expedited
		 *     - should succeed when supported by running kernel
		 *     - or fail with errno=EINVAL if unsupported and forced
		 */
		.testname = "cmd_private_expedited_register_success",
		.command = MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EINVAL,
	},
	{
		/*
		 * case 05) private expedited barrier with registration
		 *     - should succeed due to existing registration
		 *     - or fail with errno=EINVAL if unsupported and forced
		 *     - NOTE: commit 70216e18e5 (v4.16-rc1) changed behavior:
		 *     -       (a) if unsupported, and forced, < 4.16 , errno is EINVAL
		 *     -       (b) if unsupported, and forced, >= 4.16, errno is EPERM
		 */
		.testname = "cmd_private_expedited_success",
		.needregister = MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED,
		.command = MEMBARRIER_CMD_PRIVATE_EXPEDITED,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EPERM,
	},
	/*
	 * commit 70216e18e5 (v4.16-rc1) added cases 06, 07 and 08 features:
	 */
	{
		/*
		 * case 06) private expedited sync core barrier with no registrations
		 *     - should fail with errno=EPERM due to no registrations
		 *     - or be skipped if unsupported by running kernel
		 */
		.testname = "cmd_private_expedited_sync_core_fail",
		.command = MEMBARRIER_CMD_PRIVATE_EXPEDITED_SYNC_CORE,
		.flags = 0,
		.exp_ret = -1,
		.exp_errno = EPERM,
	},
	{
		/*
		 * case 07) register private expedited sync core
		 *     - should succeed when supported by running kernel
		 *     - or fail with errno=EINVAL if unsupported and forced
		 */
		.testname = "cmd_private_expedited_sync_core_register_success",
		.command = MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED_SYNC_CORE,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EINVAL,
	},
	{
		/*
		 * case 08) private expedited sync core barrier with registration
		 *     - should succeed due to existing registration
		 *     - or fail with errno=EINVAL if unsupported and forced
		 */
		.testname = "cmd_private_expedited_sync_core_success",
		.needregister = MEMBARRIER_CMD_REGISTER_PRIVATE_EXPEDITED_SYNC_CORE,
		.command = MEMBARRIER_CMD_PRIVATE_EXPEDITED_SYNC_CORE,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EINVAL,
	},
	/*
	 * commit c5f58bd58f4 (v4.16-rc1) added cases 09, 10 and 11 features:
	 */
	{
		/*
		 * case 09) global expedited barrier with no registrations
		 *     - should never fail due to no registrations
		 *     - or be skipped if unsupported by running kernel
		 */
		.testname = "cmd_global_expedited_success",
		.command = MEMBARRIER_CMD_GLOBAL_EXPEDITED,
		.flags = 0,
		.exp_ret = 0,
	},
	{
		/*
		 * case 10) register global expedited
		 *     - should succeed when supported by running kernel
		 *     - or fail with errno=EINVAL if unsupported and forced
		 */
		.testname = "cmd_global_expedited_register_success",
		.command = MEMBARRIER_CMD_REGISTER_GLOBAL_EXPEDITED,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EINVAL,
	},
	{
		/*
		 * case 11) global expedited barrier with registration
		 *     - should also succeed with registrations
		 *     - or fail with errno=EINVAL if unsupported and forced
		 */
		.testname = "cmd_global_expedited_success",
		.needregister = MEMBARRIER_CMD_REGISTER_GLOBAL_EXPEDITED,
		.command = MEMBARRIER_CMD_GLOBAL_EXPEDITED,
		.flags = 0,
		.exp_ret = 0,
		.force = 1,
		.force_exp_errno = EINVAL,
	},
};

#define passed_ok(_test)                                                       \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s passed.\n", _test.testname);        \
        return;                                                                \
    } while (0)

#define passed_unexpec(_test)                                                  \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s passed unexpectedly. "              \
            "ret = %ld with errno %d were expected. (force: %d)\n",            \
            _test.testname, _test.exp_ret, _test.exp_errno,                    \
            _test.force);                                                      \
        return;                                                                \
    } while (0)

#define failed_ok(_test)                                                       \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s failed as "                         \
            "expected.\n", _test.testname);                                    \
        return;                                                                \
    } while (0)

#define failed_ok_unsupported(_test)                                           \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s failed as expected.\n"              \
            "(unsupported)", _test.testname);                                  \
        return;                                                                \
    } while (0)

#define failed_not_ok(_test, _gotret, _goterr)                                 \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s failed. "                           \
            "ret = %d when expected was %ld. "                                 \
            "errno = %d when expected was %d. (force: %d)\n",                  \
            _test.testname, _gotret, _test.exp_ret, _goterr,                   \
            _test.exp_errno, _test.force);                                     \
        return;                                                                \
    } while (0)

#define failed_unexpec(_test, _gotret, _goterr)                                \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s failed unexpectedly. "              \
            "Got ret = %d with errno %d. (force: %d)\n",                       \
            _test.testname, _gotret, _goterr, _test.force);                    \
        return;                                                                \
    } while (0)

#define skipped(_test)                                                         \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s skipped (unsupp)\n",                \
            _test.testname);                                                   \
        return;                                                                \
    } while (0)

#define skipped_fail(_test)                                                    \
    do {                                                                       \
        fprintf(stdout, "membarrier(2): %s reported as "                       \
            "unsupported\n", _test.testname);                                  \
        return;                                                                \
    } while (0)

static int
sys_membarrier(int cmd, int flags)
{
	return syscall(__NR_membarrier, cmd, flags);
}

static void
test_membarrier_setup(void)
{
	size_t i;
	int ret;

	ret = sys_membarrier(MEMBARRIER_CMD_QUERY, 0);

	if (ret < 0) {
		if (errno == ENOSYS)
			fprintf(stdout, "membarrier(2): not supported\n");
	}

	for (i = 0; i < ARRAY_SIZE(tc); i++) {
		if ((tc[i].command > 0) && (ret & tc[i].command))
			tc[i].enabled = 1;
	}
}

static void
test_membarrier_run(unsigned int i)
{
	int ret, err = 0;

	/* not enabled and not enforced: test is skipped */

	if (!tc[i].enabled && !tc[i].force) {

		if (tc[i].always == 0)
			skipped(tc[i]);

		skipped_fail(tc[i]);
	}

	/* iterations: registration needed for some cases */

	if (tc[i].needregister && tc[i].enabled) {
		ret = sys_membarrier(tc[i].needregister, 0);

		if (ret < 0) {
			fprintf(stdout, "membarrier(2): %s could not"
			        "register\n", tc[i].testname);
		}
	}

	ret = sys_membarrier(tc[i].command, tc[i].flags);
	err = errno;

	/* enabled and not enforced: regular expected results only */

	if (tc[i].enabled && !tc[i].force) {

		if (ret >= 0 && tc[i].exp_ret == ret)
			passed_ok(tc[i]);

		if (ret < 0) {
			if (tc[i].exp_ret == ret)
				failed_ok(tc[i]);
			else
				failed_not_ok(tc[i], ret, err);
		}
	}

	/* not enabled and enforced: failure and expected errors */

	if (!tc[i].enabled && tc[i].force) {

		if (ret >= 0)
			passed_unexpec(tc[i]);

		if (ret < 0) {
			if (tc[i].force_exp_errno == err)
				failed_ok_unsupported(tc[i]);
			else
				failed_unexpec(tc[i], ret, err);
		}
	}

	/* enabled and enforced: tricky */

	if (tc[i].enabled && tc[i].force) {

		if (ret >= 0) {
			if (tc[i].exp_ret == ret)
				passed_ok(tc[i]);
			else
				passed_unexpec(tc[i]);
		}

		if (ret < 0) {

			if (tc[i].exp_ret == ret) {

				if (tc[i].exp_errno == err)
					failed_ok(tc[i]);
				else
					failed_unexpec(tc[i], ret, err);
			}

			/* unknown on force failure if enabled and forced */
			failed_unexpec(tc[i], ret, err);
		}
	}
}

int
main(int argc, char **argv)
{
	size_t i;

	test_membarrier_setup();

	for (i = 0; i < ARRAY_SIZE(tc); i++)
		test_membarrier_run(i);

	return 0;
}
