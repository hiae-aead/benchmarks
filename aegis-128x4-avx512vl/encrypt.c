#include <limits.h>
#include <stdint.h>
#include <string.h>

#include "api.h"
#include "common.h"
#include "crypto_aead.h"
#include "crypto_declassify.h"
#include "crypto_verify_16.h"
#include "crypto_verify_32.h"

#ifdef __clang__
#    pragma clang attribute push(__attribute__((target("aes,vaes,avx512f,avx512vl"))), \
                                 apply_to = function)
#elif defined(__GNUC__)
#    pragma GCC target("aes,vaes,avx512f,avx512vl")
#endif

#include <immintrin.h>

#define AES_BLOCK_LENGTH 64

/* Two 256-bit halves expose independent AES chains on CPUs that split 512-bit instructions.
 * AVX512VL preserves access to the extra registers and ternary logic instructions. */
typedef struct {
    __m256i b0;
    __m256i b1;
} aes_block_t;

static inline aes_block_t
AES_BLOCK_XOR(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_xor_si256(a.b0, b.b0), _mm256_xor_si256(a.b1, b.b1) };
}

static inline aes_block_t
AES_BLOCK_XOR3(const aes_block_t a, const aes_block_t b, const aes_block_t c)
{
    return (aes_block_t) { _mm256_ternarylogic_epi64(a.b0, b.b0, c.b0, 0x96),
                          _mm256_ternarylogic_epi64(a.b1, b.b1, c.b1, 0x96) };
}

static inline aes_block_t
AES_BLOCK_AND(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_and_si256(a.b0, b.b0), _mm256_and_si256(a.b1, b.b1) };
}

static inline aes_block_t
AES_BLOCK_LOAD(const uint8_t *a)
{
    return (aes_block_t) { _mm256_loadu_si256((const __m256i *) (const void *) a),
                          _mm256_loadu_si256((const __m256i *) (const void *) (a + 32)) };
}

static inline aes_block_t
AES_BLOCK_LOAD_64x2(uint64_t a, uint64_t b)
{
    const __m256i t = _mm256_broadcastsi128_si256(_mm_set_epi64x((long long) a, (long long) b));
    return (aes_block_t) { t, t };
}

static inline aes_block_t
aes_block_broadcast128(const uint8_t *a)
{
    const __m256i t = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *) (const void *) a));
    return (aes_block_t) { t, t };
}

#define AES_BLOCK_BROADCAST128(A) aes_block_broadcast128(A)

static inline void
AES_BLOCK_STORE(uint8_t *a, const aes_block_t b)
{
    _mm256_storeu_si256((__m256i *) (void *) a, b.b0);
    _mm256_storeu_si256((__m256i *) (void *) (a + 32), b.b1);
}

static inline aes_block_t
AES_ENC(const aes_block_t a, const aes_block_t b)
{
    return (aes_block_t) { _mm256_aesenc_epi128(a.b0, b.b0), _mm256_aesenc_epi128(a.b1, b.b1) };
}

static inline aes_block_t
AES_ENC0(const aes_block_t a)
{
    return (aes_block_t) { _mm256_aesenc_epi128(a.b0, _mm256_setzero_si256()),
                          _mm256_aesenc_epi128(a.b1, _mm256_setzero_si256()) };
}

static inline void
aegis128x4_update(aes_block_t *const state, const aes_block_t d1, const aes_block_t d2)
{
    aes_block_t tmp;

    tmp      = state[7];
    state[7] = AES_ENC(state[6], state[7]);
    state[6] = AES_ENC(state[5], state[6]);
    state[5] = AES_ENC(state[4], state[5]);
    /* AESENC(x, 0) can start before the message XOR and combine both XORs afterward. */
    state[4] = AES_BLOCK_XOR3(AES_ENC0(state[3]), state[4], d2);
    state[3] = AES_ENC(state[2], state[3]);
    state[2] = AES_ENC(state[1], state[2]);
    state[1] = AES_ENC(state[0], state[1]);
    state[0] = AES_BLOCK_XOR3(AES_ENC0(tmp), state[0], d1);
}

#include "128x4-common.h"

#ifdef __clang__
#    pragma clang attribute pop
#endif
