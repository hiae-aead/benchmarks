#include "rocca-s.h"
#include <stdio.h>
#include <string.h>

#define MAX_LEN 4097

static int
check_equal(const void *actual, const void *expected, size_t size, const char *name)
{
    if (memcmp(actual, expected, size) != 0) {
        fprintf(stderr, "%s failed at length %zu\n", name, size);
        return 1;
    }
    return 0;
}

static int
check_hex(const uint8_t *actual, size_t size, const char *expected, const char *name)
{
    static const char hex[] = "0123456789abcdef";
    for (size_t i = 0; i < size; i++) {
        if (hex[actual[i] >> 4] != expected[i * 2] ||
            hex[actual[i] & 15] != expected[i * 2 + 1]) {
            fprintf(stderr, "%s failed at byte %zu\n", name, i);
            return 1;
        }
    }
    return 0;
}

static int
test_aead(void)
{
    ROCCA_ALIGN uint8_t key[ROCCA_KEY_SIZE], iv[ROCCA_IV_SIZE], ad[37];
    ROCCA_ALIGN uint8_t msg[65], ct[65], dec[65];
    ROCCA_ALIGN uint8_t tag[ROCCA_TAG_SIZE], dec_tag[ROCCA_TAG_SIZE];
    ROCCA_ALIGN rocca_context ctx;
    const char *expected_ct =
        "ae9676303a87bbef945ba10678b146a6"
        "04683210835ec9f401f207c451f49f73"
        "b289114be9b075d7e45eb2ce244948b9"
        "ca342c1963753899ee8907d62dba4f96"
        "8b";
    const char *expected_tag =
        "d61da46f4ed042599691aa7d4d198596"
        "79dc2b918188e3b254fc48b1c201fe89";

    for (size_t i = 0; i < sizeof key; i++) key[i] = (uint8_t) i;
    for (size_t i = 0; i < sizeof iv; i++) iv[i] = (uint8_t) (3 * i + 7);
    for (size_t i = 0; i < sizeof ad; i++) ad[i] = (uint8_t) (5 * i + 11);
    for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t) (7 * i + 13);

    rocca_init(&ctx, key, iv);
    rocca_add_ad(&ctx, ad, sizeof ad);
    rocca_encrypt(&ctx, ct, msg, sizeof msg);
    rocca_tag(&ctx, tag);
    if (check_hex(ct, sizeof ct, expected_ct, "AEAD ciphertext") ||
        check_hex(tag, sizeof tag, expected_tag, "AEAD tag")) {
        return 1;
    }

    rocca_init(&ctx, key, iv);
    rocca_add_ad(&ctx, ad, sizeof ad);
    rocca_decrypt(&ctx, dec, ct, sizeof ct);
    rocca_tag(&ctx, dec_tag);
    return check_equal(dec, msg, sizeof msg, "AEAD decryption") ||
           check_equal(dec_tag, tag, sizeof tag, "AEAD decryption tag");
}

static int
test_stream(size_t size, unsigned variant)
{
    ROCCA_ALIGN uint8_t key[ROCCA_KEY_SIZE], iv[ROCCA_IV_SIZE];
    ROCCA_ALIGN uint8_t msg[MAX_LEN], zeros[MAX_LEN] = {0};
    ROCCA_ALIGN uint8_t stream[MAX_LEN], expected[MAX_LEN], ct[MAX_LEN + 64];
    ROCCA_ALIGN uint8_t tag[ROCCA_TAG_SIZE], expected_tag[ROCCA_TAG_SIZE];
    ROCCA_ALIGN rocca_context ctx, reference;

    for (size_t i = 0; i < sizeof key; i++) key[i] = (uint8_t) (i + variant);
    for (size_t i = 0; i < sizeof iv; i++) iv[i] = (uint8_t) (3 * i + variant);
    for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t) (7 * i + variant + 1);
    if (((uintptr_t) ctx.key | (uintptr_t) ctx.state | (uintptr_t) key |
         (uintptr_t) iv | (uintptr_t) msg | (uintptr_t) ct) % 64 != 0) {
        fputs("Buffer alignment failed\n", stderr);
        return 1;
    }

    rocca_init(&reference, key, iv);
    rocca_encrypt(&reference, stream, zeros, size);
    for (size_t i = 0; i < size; i++) expected[i] = stream[i] ^ msg[i];

    memset(ct, 0xa5, sizeof ct);
    rocca_init(&ctx, key, iv);
    rocca_stream_xor(&ctx, ct, msg, size);
    if (check_equal(ct, expected, size, "Stream XOR") ||
        check_equal(ctx.state, reference.state, sizeof ctx.state, "Zero-absorption state") ||
        ctx.size_m != size) {
        return 1;
    }
    for (size_t i = size; i < sizeof ct; i++) {
        if (ct[i] != 0xa5) {
            fprintf(stderr, "Stream output exceeded length %zu\n", size);
            return 1;
        }
    }
    rocca_tag(&ctx, tag);
    rocca_tag(&reference, expected_tag);
    if (check_equal(tag, expected_tag, sizeof tag, "Zero-absorption tag")) return 1;

    rocca_init(&ctx, key, iv);
    rocca_stream_xor(&ctx, ct, ct, size);
    if (check_equal(ct, msg, size, "In-place stream decryption")) return 1;
    rocca_init(&ctx, key, iv);
    rocca_stream_xor(&ctx, ct, ct, size);
    if (check_equal(ct, expected, size, "In-place stream encryption")) return 1;

    rocca_init(&ctx, key, iv);
    size_t split = size / ROCCA_MSG_BLOCK_SIZE * ROCCA_MSG_BLOCK_SIZE;
    rocca_stream_xor(&ctx, ct, msg, split);
    rocca_stream_xor(&ctx, ct + split, msg + split, size - split);
    return check_equal(ct, expected, size, "Stream continuation");
}

int
main(void)
{
    const size_t larger_sizes[] = {255, 256, 257, 1023, 1024, 1025, 4096, 4097};
    if (test_aead()) return 1;
    for (unsigned variant = 0; variant < 3; variant++) {
        for (size_t size = 0; size <= 129; size++) {
            if (test_stream(size, variant)) return 1;
        }
        for (size_t i = 0; i < sizeof larger_sizes / sizeof larger_sizes[0]; i++) {
            if (test_stream(larger_sizes[i], variant)) return 1;
        }
    }
    puts("Rocca-S AEAD and stream XOR tests passed");
    return 0;
}
