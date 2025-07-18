#include "crypto_aead.h"

/* Force ARM crypto extensions since we're on ARM with AES support */
#ifdef __aarch64__
#ifndef __ARM_FEATURE_CRYPTO
#define __ARM_FEATURE_CRYPTO 1
#endif
#endif

#include "HiAE_amalgamated.c"

int crypto_aead_encrypt(unsigned char *c, unsigned long long *clen,
                       const unsigned char *m, unsigned long long mlen,
                       const unsigned char *ad, unsigned long long adlen,
                       const unsigned char *nsec,
                       const unsigned char *npub,
                       const unsigned char *k)
{
    (void)nsec; /* Not used in HiAE */
    
    if (!c || !clen || !npub || !k) {
        return -1;
    }
    
    if (mlen > 0 && !m) {
        return -1;
    }
    
    if (adlen > 0 && !ad) {
        return -1;
    }
    
    /* HiAE outputs ciphertext and tag separately */
    uint8_t *tag = c + mlen;
    
    int ret = HiAE_encrypt(k, npub, m, c, mlen, ad, adlen, tag);
    
    if (ret == 0) {
        *clen = mlen + CRYPTO_ABYTES;
    }
    
    return ret;
}

int crypto_aead_decrypt(unsigned char *m, unsigned long long *mlen,
                       unsigned char *nsec,
                       const unsigned char *c, unsigned long long clen,
                       const unsigned char *ad, unsigned long long adlen,
                       const unsigned char *npub,
                       const unsigned char *k)
{
    (void)nsec; /* Not used in HiAE */
    
    if (!c || !npub || !k) {
        return -1;
    }
    
    if (clen < CRYPTO_ABYTES) {
        return -1;
    }
    
    unsigned long long msg_len = clen - CRYPTO_ABYTES;
    
    if (msg_len > 0 && !m) {
        return -1;
    }
    
    if (adlen > 0 && !ad) {
        return -1;
    }
    
    /* HiAE expects ciphertext and tag separately */
    const uint8_t *tag = c + msg_len;
    
    int ret = HiAE_decrypt(k, npub, m, c, msg_len, ad, adlen, tag);
    
    if (ret == 0 && mlen) {
        *mlen = msg_len;
    }
    
    return ret;
}