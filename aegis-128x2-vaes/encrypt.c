#include <limits.h>
#include <stdint.h>
#include <string.h>

#include "api.h"
#include "common.h"
#include "crypto_aead.h"
#include "crypto_declassify.h"
#include "crypto_verify_16.h"
#include "crypto_verify_32.h"

#if defined(__x86_64__) || defined(_M_X64)

#include <immintrin.h>

#ifdef __clang__
#    pragma clang attribute push(__attribute__((target("vaes,avx2,aes"))), apply_to = function)
#elif defined(__GNUC__)
#    pragma GCC target("vaes,avx2,aes")
#endif

#define AES_BLOCK_LENGTH 32

typedef struct {
    __m256i b;
} aes_block_t;

static inline aes_block_t
AES_BLOCK_XOR(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_xor_si256(a.b, b.b) };
}

static inline aes_block_t
AES_BLOCK_AND(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_and_si256(a.b, b.b) };
}

static inline aes_block_t
AES_BLOCK_LOAD(const uint8_t *a)
{
    return (aes_block_t) { _mm256_loadu_si256((const __m256i *)a) };
}

static inline aes_block_t
AES_BLOCK_LOAD_64x2(uint64_t a, uint64_t b)
{
    const __m128i t = _mm_set_epi64x(a, b);
    return (aes_block_t) { _mm256_broadcastsi128_si256(t) };
}

static inline void
AES_BLOCK_STORE(uint8_t *a, const aes_block_t b)
{
    _mm256_storeu_si256((__m256i *)a, b.b);
}

static inline aes_block_t
AES_ENC(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_aesenc_epi128(a.b, b.b) };
}

static inline void
aegis128x2_update(aes_block_t *const state, const aes_block_t d1, const aes_block_t d2)
{
    aes_block_t tmp;

    tmp      = state[7];
    state[7] = AES_ENC(state[6], state[7]);
    state[6] = AES_ENC(state[5], state[6]);
    state[5] = AES_ENC(state[4], state[5]);
    state[4] = AES_ENC(state[3], state[4]);
    state[3] = AES_ENC(state[2], state[3]);
    state[2] = AES_ENC(state[1], state[2]);
    state[1] = AES_ENC(state[0], state[1]);
    state[0] = AES_ENC(tmp, state[0]);

    state[0] = AES_BLOCK_XOR(state[0], d1);
    state[4] = AES_BLOCK_XOR(state[4], d2);
}

#include "128x2-common.h"

#ifdef __clang__
#    pragma clang attribute pop
#endif

#else // !x86_64
#error "VAES implementation requires x86-64 architecture. Use aegis-128x2-arm for ARM platforms."
#endif // x86_64 check