#include <inttypes.h>

#define CONS 0x7b

int
main(void)
{
    union {

        uint8_t  u8;
        uint16_t u16;
        uint16_t u32;
        uint16_t u64;

    } u = { .u64 = CONS };


    if (((uint8_t) u.u8  != CONS) ||
        ((uint8_t) u.u16 != CONS) ||
        ((uint8_t) u.u32 != CONS) ||
        ((uint8_t) u.u64 != CONS))
    {
        return(1);
    }

    return 0;
}
