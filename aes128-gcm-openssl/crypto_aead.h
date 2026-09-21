#ifndef CRYPTO_AEAD_H
#define CRYPTO_AEAD_H

#include <openssl/evp.h>
#include <stddef.h>

#ifndef CRYPTO_ALIGN
#    if defined(_MSC_VER)
#        define CRYPTO_ALIGN(x) __declspec(align(x))
#    else
#        define CRYPTO_ALIGN(x) __attribute__((aligned(x)))
#    endif
#endif

/* Encrypt or decrypt by XORing with the AES-CTR keystream, without
 * authentication. */
int crypto_stream_xor(unsigned char *out, const unsigned char *in, unsigned long long len,
                      const unsigned char *npub, const unsigned char *k);

int crypto_aead_encrypt(unsigned char *c, unsigned long long *clen, const unsigned char *m,
                        unsigned long long mlen, const unsigned char *ad, unsigned long long adlen,
                        const unsigned char *nsec, const unsigned char *npub,
                        const unsigned char *k);

int crypto_aead_decrypt(unsigned char *m, unsigned long long *mlen, unsigned char *nsec,
                        const unsigned char *c, unsigned long long clen, const unsigned char *ad,
                        unsigned long long adlen, const unsigned char *npub,
                        const unsigned char *k);

// Bulk encryption functions (without key setup)
int crypto_aead_encrypt_bulk(EVP_CIPHER_CTX *ctx, unsigned char *c, unsigned long long *clen,
                             const unsigned char *m, unsigned long long mlen,
                             const unsigned char *ad, unsigned long long adlen,
                             const unsigned char *nsec, const unsigned char *npub,
                             const unsigned char *k);

int crypto_aead_decrypt_bulk(EVP_CIPHER_CTX *ctx, unsigned char *m, unsigned long long *mlen,
                             unsigned char *nsec, const unsigned char *c, unsigned long long clen,
                             const unsigned char *ad, unsigned long long adlen,
                             const unsigned char *npub, const unsigned char *k);

#endif
