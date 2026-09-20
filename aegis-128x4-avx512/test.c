#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"
#include "crypto_aead.h"
#include "../aegis-stream-test.h"

#define CHECK(condition)                                                       \
    do {                                                                       \
        if (!(condition)) {                                                    \
            fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #condition);      \
            return 1;                                                          \
        }                                                                      \
    } while (0)

/* Tags from libaegis 7cc9284, with equal message and associated-data lengths. */
static const struct {
    size_t length;
    const char *tag;
} vectors[] = {
    {     0, "a4b25437f4be93cfa856a2f27e4416b42cac79fd4698f2cdbe6af25673e10a68" },
    {     1, "ec3592c891b54f74c8321ef8372a76f8c8f91f072540fd8c386899d108cfd337" },
    {   127, "373a203f3cf893c5183e787332b54edcca9cde17e5a1b925dfcb68d505551e55" },
    {   128, "ac41c05778a455bf4162e92527774faff103635f89a8c6abe8f4d3b4cb7e7b34" },
    {   129, "cfbccb2da96630f0eb30cbb57cfc55d32dc0db40e73b7e92c7816d03ade55b55" },
    {   255, "916fc39211001fdbb855fdc0af06c424342a6fb6afaebdc237f3a76498fb29e3" },
    {   256, "91c5a93e3985a968a0a9c55ca29e3d6007984de56eaa2465195e302d5510304a" },
    {   257, "9695aceb5297541918a129f18b1dabeca57115028a2db4d3023db977c0bbdd3b" },
    {   511, "9a57035cb02d748452477e0944e86c9a11fd94d8e98fec4985bfc251c07bca30" },
    {   512, "efb954de367d05af872336e29ce9aa0cf496d801fd83826f5fb399fd47923d36" },
    {   513, "7b48ee0885c632182f264d1ba585a64aee414838f69795b4b8d0ccc0c0788830" },
    {  1023, "cecf20289486371dca9ca436c09c2f5934006a4abd9d9adac6570987954bd596" },
    {  1024, "5265725b3811f0e9fd79187720c7bc8d5a022b3fd9e1428f2f7960747f9d3ee0" },
    {  1025, "14af9999c92dc3869378d2cc355491ac40e8f0144271d1ec493c6a3de88ead1c" },
    { 65536, "e78ba0167e0fd118e40f8637d2d926104e3d1f996098ee90b4525c697d4b27fa" },
};

static int
matches_hex(const unsigned char *bytes, size_t length, const char *expected)
{
    static const char digits[] = "0123456789abcdef";
    size_t i;

    if (strlen(expected) != 2 * length) {
        return 0;
    }
    for (i = 0; i < length; i++) {
        if (expected[2 * i] != digits[bytes[i] >> 4] ||
            expected[2 * i + 1] != digits[bytes[i] & 15]) {
            return 0;
        }
    }
    return 1;
}

static unsigned char *
unaligned_buffer(size_t length)
{
    unsigned char *storage = malloc(length + 2);

    if (storage == NULL) {
        perror("malloc");
        exit(1);
    }
    memset(storage, 0xa5, length + 2);
    return storage + 1;
}

static int
guards_intact(const unsigned char *buffer, size_t length)
{
    return buffer[-1] == 0xa5 && buffer[length] == 0xa5;
}

static int
is_zero(const unsigned char *buffer, size_t length)
{
    size_t i;

    for (i = 0; i < length; i++) {
        if (buffer[i] != 0) {
            return 0;
        }
    }
    return 1;
}

static int
reject(const unsigned char *ciphertext, size_t clen, const unsigned char *ad, size_t adlen,
       const unsigned char *nonce, const unsigned char *key, unsigned char *decrypted)
{
    const size_t length = clen - CRYPTO_ABYTES;
    unsigned long long mlen = 123;

    memset(decrypted, 0xa5, length);
    CHECK(crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, adlen,
                              nonce, key) == -1);
    CHECK(mlen == 0 && is_zero(decrypted, length));
    CHECK(guards_intact(decrypted, length));
    mlen = 123;
    CHECK(crypto_aead_decrypt(NULL, &mlen, NULL, ciphertext, clen, ad, adlen,
                              nonce, key) == -1);
    CHECK(mlen == 0);
    return 0;
}

static int
test_vector(const unsigned char *key, const unsigned char *nonce)
{
    static const char ciphertext_hex[] =
        "e836118562f4479c9d35c17356a833114c21f9aa39e4dda5e5c87f4152a00fce9"
        "a7c38f832eafe8b1c12f8a7cf12a81a1ad8a9c24ba9dedfbdaa586ffea67ddc8"
        "01ea97d9ab4a872f42d0e352e2713dacd609f9442c17517c5a29daf3e2a3fac4ff"
        "6b1380c4e46df7b086af6ce6bc1ed594b8dd64aed2a7e";
    static const char tag_hex[] =
        "69abf0f64a137dd6e122478d777e98bc422823006cf57f5ee822dd78397230b2";
    unsigned char message[120], ad[8], ciphertext[120 + CRYPTO_ABYTES], decrypted[120];
    unsigned long long clen, mlen;
    size_t i;

    for (i = 0; i < sizeof message; i++) {
        message[i] = (unsigned char) (4 + i % 4);
    }
    for (i = 0; i < sizeof ad; i++) {
        ad[i] = (unsigned char) (1 + i % 4);
    }
    CHECK(crypto_aead_encrypt(ciphertext, &clen, message, sizeof message, ad, sizeof ad,
                              NULL, nonce, key) == 0);
    CHECK(clen == sizeof ciphertext);
    CHECK(matches_hex(ciphertext, sizeof message, ciphertext_hex));
    CHECK(matches_hex(ciphertext + sizeof message, CRYPTO_ABYTES, tag_hex));
    CHECK(crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, sizeof ad,
                              nonce, key) == 0);
    CHECK(mlen == sizeof message && memcmp(message, decrypted, sizeof message) == 0);
    return 0;
}

static int
test_lengths(size_t length, size_t adlen, const char *expected_tag,
             const unsigned char *key, const unsigned char *nonce)
{
    const size_t capacity = length + CRYPTO_ABYTES;
    unsigned char *message = unaligned_buffer(length);
    unsigned char *ad = unaligned_buffer(adlen);
    unsigned char *ciphertext = unaligned_buffer(capacity);
    unsigned char *decrypted = unaligned_buffer(length);
    unsigned char *in_place = unaligned_buffer(capacity);
    unsigned long long clen = 123, mlen = 123;
    size_t i;

    for (i = 0; i < length; i++) {
        message[i] = (unsigned char) (29 * i + 7);
    }
    for (i = 0; i < adlen; i++) {
        ad[i] = (unsigned char) (31 * i + 11);
    }
    CHECK(crypto_aead_encrypt(ciphertext, &clen, message, length, ad, adlen,
                              NULL, nonce, key) == 0);
    CHECK(clen == capacity);
    if (expected_tag != NULL) {
        CHECK(matches_hex(ciphertext + length, CRYPTO_ABYTES, expected_tag));
    }
    CHECK(crypto_aead_decrypt(decrypted, &mlen, NULL, ciphertext, clen, ad, adlen,
                              nonce, key) == 0);
    CHECK(mlen == length && memcmp(message, decrypted, length) == 0);
    CHECK(crypto_aead_decrypt(NULL, &mlen, NULL, ciphertext, clen, ad, adlen,
                              nonce, key) == 0);
    CHECK(mlen == length);
    memcpy(in_place, message, length);
    CHECK(crypto_aead_encrypt(in_place, NULL, in_place, length, ad, adlen,
                              NULL, nonce, key) == 0);
    CHECK(memcmp(in_place, ciphertext, capacity) == 0);
    CHECK(crypto_aead_decrypt(in_place, NULL, NULL, in_place, capacity, ad, adlen,
                              nonce, key) == 0);
    CHECK(memcmp(in_place, message, length) == 0);

    for (i = 0; i < CRYPTO_ABYTES; i++) {
        ciphertext[length + i] ^= 1;
        CHECK(reject(ciphertext, capacity, ad, adlen, nonce, key, decrypted) == 0);
        ciphertext[length + i] ^= 1;
    }
    if (length != 0) {
        ciphertext[length / 2] ^= 1;
        CHECK(reject(ciphertext, capacity, ad, adlen, nonce, key, decrypted) == 0);
        ciphertext[length / 2] ^= 1;
    }
    if (adlen != 0) {
        ad[adlen / 2] ^= 1;
        CHECK(reject(ciphertext, capacity, ad, adlen, nonce, key, decrypted) == 0);
        ad[adlen / 2] ^= 1;
    }
    memcpy(in_place, ciphertext, capacity);
    in_place[capacity - 1] ^= 1;
    mlen = 123;
    CHECK(crypto_aead_decrypt(in_place, &mlen, NULL, in_place, capacity, ad, adlen,
                              nonce, key) == -1);
    CHECK(mlen == 0 && is_zero(in_place, length));
    CHECK(guards_intact(message, length) && guards_intact(ad, adlen));
    CHECK(guards_intact(ciphertext, capacity) && guards_intact(decrypted, length));
    CHECK(guards_intact(in_place, capacity));

    free(message - 1);
    free(ad - 1);
    free(ciphertext - 1);
    free(decrypted - 1);
    free(in_place - 1);
    return 0;
}

static int
test_short_ciphertext(const unsigned char *key, const unsigned char *nonce)
{
    unsigned char ciphertext[CRYPTO_ABYTES] = { 0 }, decrypted = 0xa5;
    unsigned long long mlen;
    size_t length;

    for (length = 0; length < CRYPTO_ABYTES; length++) {
        mlen = 123;
        CHECK(crypto_aead_decrypt(&decrypted, &mlen, NULL, ciphertext, length, NULL, 0,
                                  nonce, key) == -1);
        CHECK(mlen == 0 && decrypted == 0xa5);
    }
    return 0;
}

int
main(void)
{
    unsigned char *key = unaligned_buffer(CRYPTO_KEYBYTES);
    unsigned char *nonce = unaligned_buffer(CRYPTO_NPUBBYTES);
    const size_t count = sizeof vectors / sizeof vectors[0];
    size_t i, j;

    for (i = 0; i < CRYPTO_KEYBYTES; i++) {
        key[i] = (unsigned char) i;
    }
    for (i = 0; i < CRYPTO_NPUBBYTES; i++) {
        nonce[i] = (unsigned char) (i + 16);
    }
    CHECK(test_stream_xor() == 0);
    CHECK(test_vector(key, nonce) == 0);
    CHECK(test_short_ciphertext(key, nonce) == 0);
    for (i = 0; i < count; i++) {
        for (j = 0; j < count; j++) {
            if (test_lengths(vectors[i].length, vectors[j].length,
                             i == j ? vectors[i].tag : NULL, key, nonce) != 0) {
                fprintf(stderr, "Failed with message length %zu and AD length %zu\n",
                        vectors[i].length, vectors[j].length);
                return 1;
            }
        }
    }
    CHECK(guards_intact(key, CRYPTO_KEYBYTES) && guards_intact(nonce, CRYPTO_NPUBBYTES));
    free(key - 1);
    free(nonce - 1);
    printf("AEGIS-128X4 tests passed (%zu length pairs).\n", count * count);
    return 0;
}
