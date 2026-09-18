// Checks the code being benchmarked against known test vectors.

#include "crypto_aead.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NAME    "HiAEx2"
#define MAX_LEN 4096

typedef struct {
    const char *name;
    const char *key;
    const char *nonce;
    const char *ad;
    const char *plaintext;
    const char *ciphertext;
    const char *tag;
} TestVector;

static const TestVector test_vectors[] = {
    { .name       = "Test Vector 1: empty plaintext, no AD",
      .key        = "4b7a9c3ef8d2165a0b3e5f8c9d4a7b1e2c5f8a9d3b6e4c7f0a1d2e5b8c9f4a7d",
      .nonce      = "a5b8c2d9e3f4a7b1c8d5e9f2a3b6c7d8",
      .ad         = "",
      .plaintext  = "",
      .ciphertext = "",
      .tag        = "814466e804ffb89e586130ef8c5a09eb" },
    { .name       = "Test Vector 2: single block plaintext, no AD",
      .key        = "2f8e4d7c3b9a5e1f8d2c6b4a9f3e7d5c1b8a6f4e3d2c9b5a8f7e6d4c3b2a1f9e",
      .nonce      = "7c3e9f5a1d8b4c6f2e9a5d7b3f8c1e4a",
      .ad         = "",
      .plaintext  = "55f00fcc339669aa55f00fcc339669aa",
      .ciphertext = "b1b159fa6b6d3088a4fdb2d70aae888e",
      .tag        = "c07f5633f8125b73839805aa0e029f9e" },
    { .name       = "Test Vector 3: empty plaintext with AD",
      .key        = "9f3e7d5c4b8a2f1e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e",
      .nonce      = "3d8c7f2a5b9e4c1f8a6d3b7e5c2f9a4d",
      .ad         = "394a5b6c7d8e9fb0c1d2e3f405162738495a6b7c8d9eafc0d1e2f30415263748",
      .plaintext  = "",
      .ciphertext = "",
      .tag        = "0802b8d956e7c9cce970750b984aa2c7" },
    { .name       = "Test Vector 4: 32-byte aligned plaintext",
      .key        = "6c8f2d5a9e3b7f4c1d8a5e9f3c7b2d6a4f8e1c9b5d3a7e2f4c8b6d9a1e5f3c7d",
      .nonce      = "9a5c7e3f1b8d4a6c2e9f5b7d3a8c1e6f",
      .ad         = "",
      .plaintext  = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
      .ciphertext = "ad8a0a8a056d1584022c656b23bba01b9b39f54495681ef0764c838796b0ab90",
      .tag        = "fd86bc44dda4966a386923bd29fac27c" },
    { .name       = "Test Vector 5: single byte plaintext",
      .key        = "7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a",
      .nonce      = "2e7c9f5d3b8a4c6f1e9b5d7a3f8c2e4a",
      .ad         = "",
      .plaintext  = "ff",
      .ciphertext = "32",
      .tag        = "15a55f0bbffc3d6bc6c192db1cb19768" }
};

static int
hex_decode(uint8_t *out, size_t max_len, const char *hex)
{
    size_t len = strlen(hex) / 2;
    if (len > max_len) {
        return -1;
    }
    for (size_t i = 0; i < len; i++) {
        unsigned int byte;
        if (sscanf(hex + 2 * i, "%2x", &byte) != 1) {
            return -1;
        }
        out[i] = (uint8_t) byte;
    }
    return (int) len;
}

static const char *
run_test_vector(const TestVector *tv)
{
    static uint8_t key[CRYPTO_KEYBYTES], nonce[CRYPTO_NPUBBYTES];
    static uint8_t ad[MAX_LEN], plaintext[MAX_LEN], decrypted[MAX_LEN];
    static uint8_t expected[MAX_LEN + CRYPTO_ABYTES], ciphertext[MAX_LEN + CRYPTO_ABYTES];
    unsigned long long clen, mlen;

    if (hex_decode(key, sizeof key, tv->key) != CRYPTO_KEYBYTES ||
        hex_decode(nonce, sizeof nonce, tv->nonce) != CRYPTO_NPUBBYTES) {
        return "bad key or nonce";
    }
    int ad_len = hex_decode(ad, sizeof ad, tv->ad);
    int pt_len = hex_decode(plaintext, sizeof plaintext, tv->plaintext);
    if (ad_len < 0 || pt_len < 0 || hex_decode(expected, MAX_LEN, tv->ciphertext) != pt_len ||
        hex_decode(expected + pt_len, CRYPTO_ABYTES, tv->tag) != CRYPTO_ABYTES) {
        return "bad test vector";
    }

    int ret = crypto_aead_encrypt(ciphertext, &clen, plaintext, pt_len, ad, ad_len, NULL, nonce, key);
    if (ret != 0 || clen != (unsigned long long) pt_len + CRYPTO_ABYTES || memcmp(ciphertext, expected, clen) != 0) {
        return "wrong ciphertext or tag";
    }
    ret = crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, ad_len, nonce, key);
    if (ret != 0 || mlen != (unsigned long long) pt_len || memcmp(decrypted, plaintext, pt_len) != 0) {
        return "decryption failed";
    }
    ciphertext[clen - 1] ^= 1;
    if (crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, ad_len, nonce, key) == 0) {
        return "a forged tag was accepted";
    }
    return NULL;
}

int
main(void)
{
    const size_t count  = sizeof test_vectors / sizeof test_vectors[0];
    int          failed = 0;

    for (size_t i = 0; i < count; i++) {
        const char *error = run_test_vector(&test_vectors[i]);
        if (error != NULL) {
            printf("%s: %s\n", test_vectors[i].name, error);
            failed++;
        }
    }
    printf("%s test vectors: %d passed, %d failed\n", NAME, (int) count - failed, failed);

    return failed > 0;
}
