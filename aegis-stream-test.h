#ifndef AEGIS_STREAM_TEST_H
#define AEGIS_STREAM_TEST_H

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define STREAM_CHECK(condition)                                                         \
    do {                                                                                \
        if (!(condition)) {                                                             \
            fprintf(stderr, "%s:%d: %s (length %zu, offset %zu)\n", __FILE__, __LINE__, \
                    #condition, length, offset);                                        \
            return 1;                                                                   \
        }                                                                               \
    } while (0)

static int
test_stream_xor(void)
{
    static const size_t            lengths[] = { 0,   1,   15,  16,  17,   31,   32,   33,
                                                 63,  64,  65,  127, 128,  129,  255,  256,
                                                 257, 511, 512, 513, 1023, 1024, 1025, 65536 };
    CRYPTO_ALIGN(64) unsigned char key[CRYPTO_KEYBYTES];
    CRYPTO_ALIGN(64) unsigned char nonce[CRYPTO_NPUBBYTES];
    CRYPTO_ALIGN(64) unsigned char zeros[65536] = { 0 };
    CRYPTO_ALIGN(64) unsigned char message_storage[65536 + 128];
    CRYPTO_ALIGN(64) unsigned char stream_storage[65536 + CRYPTO_ABYTES + 128];
    CRYPTO_ALIGN(64) unsigned char output_storage[65536 + 128];
    CRYPTO_ALIGN(64) unsigned char inplace_storage[65536 + CRYPTO_ABYTES + 128];
    unsigned long long             clen, mlen;
    size_t                         i, n, offset, length = 0;

    for (i = 0; i < sizeof key; i++) {
        key[i] = (unsigned char) (7 * i + 1);
    }
    for (i = 0; i < sizeof nonce; i++) {
        nonce[i] = (unsigned char) (13 * i + 2);
    }
    for (offset = 0; offset <= 1; offset++) {
        unsigned char *message = message_storage + 64 + offset;
        unsigned char *stream  = stream_storage + 64 + offset;
        unsigned char *output  = output_storage + 64 + offset;
        unsigned char *inplace = inplace_storage + 64 + offset;

        STREAM_CHECK(crypto_stream_xor(NULL, NULL, 0, nonce, key) == 0);
        if (offset == 0) {
            STREAM_CHECK(((uintptr_t) message & 63) == 0);
            STREAM_CHECK(((uintptr_t) stream & 63) == 0);
            STREAM_CHECK(((uintptr_t) output & 63) == 0);
            STREAM_CHECK(((uintptr_t) inplace & 63) == 0);
        }
        for (n = 0; n < sizeof lengths / sizeof lengths[0]; n++) {
            length = lengths[n];
            memset(message_storage, 0xa5, sizeof message_storage);
            memset(stream_storage, 0xa5, sizeof stream_storage);
            memset(output_storage, 0xa5, sizeof output_storage);
            memset(inplace_storage, 0xa5, sizeof inplace_storage);
            for (i = 0; i < length; i++) {
                message[i] = (unsigned char) (29 * i + 7);
            }
            STREAM_CHECK(
                crypto_aead_encrypt(stream, &clen, zeros, length, NULL, 0, NULL, nonce, key) == 0);
            STREAM_CHECK(clen == length + CRYPTO_ABYTES);
            STREAM_CHECK(crypto_stream_xor(output, message, length, nonce, key) == 0);
            for (i = 0; i < length; i++) {
                STREAM_CHECK(output[i] == (unsigned char) (message[i] ^ stream[i]));
                STREAM_CHECK(message[i] == (unsigned char) (29 * i + 7));
            }
            memcpy(inplace, message, length);
            STREAM_CHECK(crypto_stream_xor(inplace, inplace, length, nonce, key) == 0);
            STREAM_CHECK(memcmp(inplace, output, length) == 0);
            STREAM_CHECK(inplace[-1] == 0xa5 && inplace[length] == 0xa5);
            STREAM_CHECK(crypto_stream_xor(inplace, inplace, length, nonce, key) == 0);
            STREAM_CHECK(memcmp(inplace, message, length) == 0);
            STREAM_CHECK(message[-1] == 0xa5 && message[length] == 0xa5);
            STREAM_CHECK(output[-1] == 0xa5 && output[length] == 0xa5);
            STREAM_CHECK(inplace[-1] == 0xa5 && inplace[length] == 0xa5);
            STREAM_CHECK(stream[-1] == 0xa5 && stream[clen] == 0xa5);

            STREAM_CHECK(crypto_aead_encrypt(inplace, &clen, message, length, message, length, NULL,
                                             nonce, key) == 0);
            STREAM_CHECK(crypto_aead_decrypt(output, &mlen, NULL, inplace, clen, message, length,
                                             nonce, key) == 0);
            STREAM_CHECK(mlen == length && memcmp(output, message, length) == 0);
            inplace[clen - 1] ^= 1;
            STREAM_CHECK(crypto_aead_decrypt(output, &mlen, NULL, inplace, clen, message, length,
                                             nonce, key) == -1);
            STREAM_CHECK(mlen == 0 && memcmp(output, zeros, length) == 0);
        }
    }
    return 0;
}

#undef STREAM_CHECK

#endif
