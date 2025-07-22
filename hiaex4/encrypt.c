#include "crypto_aead.h"
#include "HiAEx4.h"

int crypto_aead_encrypt(unsigned char *c, unsigned long long *clen,
                       const unsigned char *m, unsigned long long mlen,
                       const unsigned char *ad, unsigned long long adlen,
                       const unsigned char *nsec,
                       const unsigned char *npub,
                       const unsigned char *k)
{
    (void)nsec; /* Not used in HiAEx4 */
    
    if (!c || !clen || !npub || !k) {
        return -1;
    }
    
    if (mlen > 0 && !m) {
        return -1;
    }
    
    if (adlen > 0 && !ad) {
        return -1;
    }
    
    /* HiAEx4 outputs ciphertext and tag separately */
    uint8_t *tag = c + mlen;
    
    int ret = HiAEx4_encrypt(k, npub, m, c, mlen, ad, adlen, tag);
    
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
    (void)nsec; /* Not used in HiAEx4 */
    
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
    
    /* HiAEx4 expects ciphertext and tag separately */
    const uint8_t *tag = c + msg_len;
    
    int ret = HiAEx4_decrypt(k, npub, m, c, msg_len, ad, adlen, tag);
    
    if (ret == 0 && mlen) {
        *mlen = msg_len;
    }
    
    return ret;
}