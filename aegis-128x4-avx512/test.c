#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "crypto_aead.h"
#include "api.h"

int main(void) {
    printf("AEGIS-128x4 AVX512 implementation compiled successfully!\n");
    printf("Key bytes: %d\n", CRYPTO_KEYBYTES);
    printf("Nonce bytes: %d\n", CRYPTO_NPUBBYTES);
    printf("Auth bytes: %d\n", CRYPTO_ABYTES);
    
    // Simple functionality test
    unsigned char key[CRYPTO_KEYBYTES];
    unsigned char nonce[CRYPTO_NPUBBYTES];
    unsigned char msg[64] = "Hello, AEGIS-128x4! This is a test message for encryption.";
    unsigned char ct[64 + CRYPTO_ABYTES];
    unsigned char dec[64];
    unsigned long long clen, mlen;
    
    memset(key, 1, CRYPTO_KEYBYTES);
    memset(nonce, 2, CRYPTO_NPUBBYTES);
    
    printf("Running basic encrypt/decrypt test...\n");
    
    // Encrypt
    int result = crypto_aead_encrypt(ct, &clen, msg, 64, NULL, 0, NULL, nonce, key);
    if (result != 0) {
        printf("Encryption failed!\n");
        return 1;
    }
    printf("Encryption successful, ciphertext length: %llu\n", clen);
    
    // Decrypt
    result = crypto_aead_decrypt(dec, &mlen, NULL, ct, clen, NULL, 0, nonce, key);
    if (result != 0) {
        printf("Decryption failed!\n");
        return 1;
    }
    printf("Decryption successful, message length: %llu\n", mlen);
    
    // Verify
    if (memcmp(msg, dec, 64) == 0) {
        printf("Test PASSED: Original and decrypted messages match!\n");
    } else {
        printf("Test FAILED: Messages do not match!\n");
        return 1;
    }
    
    return 0;
}