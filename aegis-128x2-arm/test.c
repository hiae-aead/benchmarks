#include <stdio.h>

#include "common.h"
#include "crypto_aead.h"
#include "../aegis-stream-test.h"

int
main(void)
{
    if (test_stream_xor() != 0) {
        return 1;
    }
    puts("AEGIS-128X2 stream XOR and AEAD tests passed.");
    return 0;
}
