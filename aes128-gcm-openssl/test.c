#include "api.h"
#include "crypto_aead.h"
#include <openssl/err.h>
#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int
test_stream_xor(void)
{
    static const size_t        lengths[]       = { 0,   1,   15,   16,   17,   31,   32,   33,  63,
                                                   64,  65,  127,  128,  129,  255,  256,  257, 511,
                                                   512, 513, 1023, 1024, 1025, 4096, 65536 };
    static const size_t        offsets[]       = { 0, 1, 63 };
    static const unsigned char first_block[16] = { 0x03, 0x88, 0xda, 0xce, 0x60, 0xb6, 0xa3, 0x92,
                                                   0xf3, 0x28, 0xc2, 0xb9, 0x71, 0xb2, 0xfe, 0x78 };
    CRYPTO_ALIGN(64) unsigned char        key[CRYPTO_KEYBYTES]    = { 0 };
    CRYPTO_ALIGN(64) unsigned char        nonce[CRYPTO_NPUBBYTES] = { 0 };
    CRYPTO_ALIGN(64) static unsigned char zeros[65536];
    CRYPTO_ALIGN(64) static unsigned char stream[65536 + CRYPTO_ABYTES];
    CRYPTO_ALIGN(64) static unsigned char input[65536 + 64];
    CRYPTO_ALIGN(64) static unsigned char output[65536 + 64];
    unsigned long long                    clen;

    if (crypto_stream_xor(output, zeros, 16, nonce, key) != 0 ||
        memcmp(output, first_block, sizeof first_block) != 0) {
        fprintf(stderr, "AES-CTR known-answer test failed\n");
        return -1;
    }
    for (size_t i = 0; i < sizeof key; i++) {
        key[i] = (unsigned char) (i * 7 + 3);
    }
    for (size_t i = 0; i < sizeof nonce; i++) {
        nonce[i] = (unsigned char) (i * 11 + 5);
    }
    for (size_t i = 0; i < sizeof input; i++) {
        input[i] = (unsigned char) (i * 13 + 7);
    }
    if (crypto_stream_xor(NULL, NULL, 0, nonce, key) != 0) {
        return -1;
    }
    for (size_t n = 0; n < sizeof lengths / sizeof lengths[0]; n++) {
        size_t len = lengths[n];
        if (crypto_aead_encrypt(stream, &clen, zeros, len, NULL, 0, NULL, nonce, key) != 0 ||
            clen != len + CRYPTO_ABYTES) {
            return -1;
        }
        for (size_t j = 0; j < sizeof offsets / sizeof offsets[0]; j++) {
            size_t               offset = offsets[j];
            unsigned char       *out    = output + offset;
            const unsigned char *in     = input + offset;

            memset(output, 0xa5, sizeof output);
            if (crypto_stream_xor(out, in, len, nonce, key) != 0) {
                return -1;
            }
            for (size_t i = 0; i < len; i++) {
                if (out[i] != (unsigned char) (in[i] ^ stream[i])) {
                    fprintf(stderr, "AES-CTR keystream mismatch at length %zu, byte %zu\n", len, i);
                    return -1;
                }
            }
            if ((offset != 0 && out[-1] != 0xa5) || out[len] != 0xa5 ||
                crypto_stream_xor(out, out, len, nonce, key) != 0 || memcmp(out, in, len) != 0) {
                fprintf(stderr, "AES-CTR bounds or in-place test failed at length %zu\n", len);
                return -1;
            }
        }
    }
    puts("AES-CTR keystream, boundary, and in-place tests passed");
    return 0;
}

void
print_hex(const char *label, const unsigned char *data, size_t len)
{
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int
main()
{
    if (test_stream_xor() != 0) {
        return 1;
    }
    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    printf("AES-128-GCM (OpenSSL) Test\n");
    printf("==========================\n\n");

    // Test vectors
    unsigned char key[CRYPTO_KEYBYTES] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
                                           0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f };

    unsigned char nonce[CRYPTO_NPUBBYTES] = { 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
                                              0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b };

    unsigned char plaintext[]   = "Hello, World! This is a test message.";
    size_t        plaintext_len = strlen((char *) plaintext);

    unsigned char ad[]   = "Additional authenticated data";
    size_t        ad_len = strlen((char *) ad);

    unsigned char      ciphertext[1024];
    unsigned char      decrypted[1024];
    unsigned long long ciphertext_len;
    unsigned long long decrypted_len;

    printf("Test 1: Basic encryption/decryption\n");
    printf("-----------------------------------\n");
    print_hex("Key", key, CRYPTO_KEYBYTES);
    print_hex("Nonce", nonce, CRYPTO_NPUBBYTES);
    printf("Plaintext: %s\n", plaintext);
    printf("AD: %s\n\n", ad);

    // Encrypt
    int result = crypto_aead_encrypt(ciphertext, &ciphertext_len, plaintext, plaintext_len, ad,
                                     ad_len, NULL, nonce, key);

    if (result != 0) {
        fprintf(stderr, "Encryption failed!\n");
        return 1;
    }

    printf("Encryption successful!\n");
    printf("Ciphertext length: %llu bytes (including %d-byte tag)\n", ciphertext_len,
           CRYPTO_ABYTES);
    print_hex("Ciphertext + Tag", ciphertext, ciphertext_len);
    printf("\n");

    // Decrypt
    result = crypto_aead_decrypt(decrypted, &decrypted_len, NULL, ciphertext, ciphertext_len, ad,
                                 ad_len, nonce, key);

    if (result != 0) {
        fprintf(stderr, "Decryption failed!\n");
        return 1;
    }

    printf("Decryption successful!\n");
    printf("Decrypted length: %llu bytes\n", decrypted_len);
    decrypted[decrypted_len] = '\0';
    printf("Decrypted text: %s\n\n", decrypted);

    // Verify
    if (decrypted_len != plaintext_len || memcmp(plaintext, decrypted, plaintext_len) != 0) {
        fprintf(stderr, "Decryption mismatch!\n");
        return 1;
    }

    printf("Test 2: Authentication failure test\n");
    printf("-----------------------------------\n");

    // Modify ciphertext
    ciphertext[0] ^= 0x01;

    result = crypto_aead_decrypt(decrypted, &decrypted_len, NULL, ciphertext, ciphertext_len, ad,
                                 ad_len, nonce, key);

    if (result == 0) {
        fprintf(stderr, "ERROR: Modified ciphertext was accepted!\n");
        return 1;
    }

    printf("Good: Modified ciphertext was rejected (authentication failed)\n\n");

    printf("Test 3: Empty plaintext\n");
    printf("-----------------------\n");

    result =
        crypto_aead_encrypt(ciphertext, &ciphertext_len, NULL, 0, ad, ad_len, NULL, nonce, key);

    if (result != 0) {
        fprintf(stderr, "Encryption of empty plaintext failed!\n");
        return 1;
    }

    printf("Empty plaintext encrypted successfully\n");
    printf("Ciphertext length: %llu bytes (tag only)\n", ciphertext_len);

    result = crypto_aead_decrypt(decrypted, &decrypted_len, NULL, ciphertext, ciphertext_len, ad,
                                 ad_len, nonce, key);

    if (result != 0 || decrypted_len != 0) {
        fprintf(stderr, "Decryption of empty plaintext failed!\n");
        return 1;
    }

    printf("Empty plaintext decrypted successfully\n\n");

    printf("All tests passed!\n");

    // Cleanup OpenSSL
    EVP_cleanup();
    ERR_free_strings();

    return 0;
}
