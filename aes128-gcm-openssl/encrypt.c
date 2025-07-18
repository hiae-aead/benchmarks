#include <string.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include "api.h"
#include "crypto_aead.h"

int crypto_aead_encrypt(
    unsigned char *c, unsigned long long *clen,
    const unsigned char *m, unsigned long long mlen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *nsec,
    const unsigned char *npub,
    const unsigned char *k)
{
    EVP_CIPHER_CTX *ctx;
    int len;
    int ciphertext_len;
    
    // Create and initialize the context
    if(!(ctx = EVP_CIPHER_CTX_new())) return -1;
    
    // Initialize the encryption operation with AES-128-GCM
    if(1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Set IV length to 12 bytes (96 bits)
    if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, CRYPTO_NPUBBYTES, NULL)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Initialize key and IV
    if(1 != EVP_EncryptInit_ex(ctx, NULL, NULL, k, npub)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Provide any AAD data
    if(adlen > 0) {
        if(1 != EVP_EncryptUpdate(ctx, NULL, &len, ad, adlen)) {
            EVP_CIPHER_CTX_free(ctx);
            return -1;
        }
    }
    
    // Provide the message to be encrypted, and obtain the encrypted output
    if(1 != EVP_EncryptUpdate(ctx, c, &len, m, mlen)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len = len;
    
    // Finalize the encryption
    if(1 != EVP_EncryptFinal_ex(ctx, c + len, &len)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len += len;
    
    // Get the tag
    if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, CRYPTO_ABYTES, c + ciphertext_len)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Clean up
    EVP_CIPHER_CTX_free(ctx);
    
    *clen = ciphertext_len + CRYPTO_ABYTES;
    return 0;
}

int crypto_aead_decrypt(
    unsigned char *m, unsigned long long *mlen,
    unsigned char *nsec,
    const unsigned char *c, unsigned long long clen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *npub,
    const unsigned char *k)
{
    EVP_CIPHER_CTX *ctx;
    int len;
    int plaintext_len;
    int ret;
    
    // Check that ciphertext length is valid
    if (clen < CRYPTO_ABYTES) return -1;
    
    // Create and initialize the context
    if(!(ctx = EVP_CIPHER_CTX_new())) return -1;
    
    // Initialize the decryption operation with AES-128-GCM
    if(!EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Set IV length
    if(!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, CRYPTO_NPUBBYTES, NULL)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Initialize key and IV
    if(!EVP_DecryptInit_ex(ctx, NULL, NULL, k, npub)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Provide any AAD data
    if(adlen > 0) {
        if(!EVP_DecryptUpdate(ctx, NULL, &len, ad, adlen)) {
            EVP_CIPHER_CTX_free(ctx);
            return -1;
        }
    }
    
    // Provide the message to be decrypted
    if(!EVP_DecryptUpdate(ctx, m, &len, c, clen - CRYPTO_ABYTES)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    plaintext_len = len;
    
    // Set expected tag value
    if(!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, CRYPTO_ABYTES, 
                           (unsigned char *)c + clen - CRYPTO_ABYTES)) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    
    // Finalize the decryption. A positive return value indicates success,
    // a return value of zero or negative indicates a failure - the verification failed.
    ret = EVP_DecryptFinal_ex(ctx, m + len, &len);
    
    // Clean up
    EVP_CIPHER_CTX_free(ctx);
    
    if(ret > 0) {
        // Success
        plaintext_len += len;
        *mlen = plaintext_len;
        return 0;
    } else {
        // Verification failed
        return -1;
    }
}

// Bulk encryption function (context reuse)
int crypto_aead_encrypt_bulk(
    EVP_CIPHER_CTX *ctx,
    unsigned char *c, unsigned long long *clen,
    const unsigned char *m, unsigned long long mlen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *nsec,
    const unsigned char *npub,
    const unsigned char *k)
{
    int len;
    int ciphertext_len;
    
    // Reset the context and set new IV (key remains the same)
    if(1 != EVP_EncryptInit_ex(ctx, NULL, NULL, NULL, npub)) {
        return -1;
    }
    
    // Provide any AAD data
    if(adlen > 0) {
        if(1 != EVP_EncryptUpdate(ctx, NULL, &len, ad, adlen)) {
            return -1;
        }
    }
    
    // Provide the message to be encrypted
    if(1 != EVP_EncryptUpdate(ctx, c, &len, m, mlen)) {
        return -1;
    }
    ciphertext_len = len;
    
    // Finalize the encryption
    if(1 != EVP_EncryptFinal_ex(ctx, c + len, &len)) {
        return -1;
    }
    ciphertext_len += len;
    
    // Get the tag
    if(1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, CRYPTO_ABYTES, c + ciphertext_len)) {
        return -1;
    }
    
    *clen = ciphertext_len + CRYPTO_ABYTES;
    return 0;
}

// Bulk decryption function (context reuse)
int crypto_aead_decrypt_bulk(
    EVP_CIPHER_CTX *ctx,
    unsigned char *m, unsigned long long *mlen,
    unsigned char *nsec,
    const unsigned char *c, unsigned long long clen,
    const unsigned char *ad, unsigned long long adlen,
    const unsigned char *npub,
    const unsigned char *k)
{
    int len;
    int plaintext_len;
    int ret;
    
    // Check that ciphertext length is valid
    if (clen < CRYPTO_ABYTES) return -1;
    
    // Reset the context and set new IV (key remains the same)
    if(!EVP_DecryptInit_ex(ctx, NULL, NULL, NULL, npub)) {
        return -1;
    }
    
    // Provide any AAD data
    if(adlen > 0) {
        if(!EVP_DecryptUpdate(ctx, NULL, &len, ad, adlen)) {
            return -1;
        }
    }
    
    // Provide the message to be decrypted
    if(!EVP_DecryptUpdate(ctx, m, &len, c, clen - CRYPTO_ABYTES)) {
        return -1;
    }
    plaintext_len = len;
    
    // Set expected tag value
    if(!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, CRYPTO_ABYTES, 
                           (unsigned char *)c + clen - CRYPTO_ABYTES)) {
        return -1;
    }
    
    // Finalize the decryption
    ret = EVP_DecryptFinal_ex(ctx, m + len, &len);
    
    if(ret > 0) {
        // Success
        plaintext_len += len;
        *mlen = plaintext_len;
        return 0;
    } else {
        // Verification failed
        return -1;
    }
}