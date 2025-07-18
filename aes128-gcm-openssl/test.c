#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include "api.h"
#include "crypto_aead.h"

void print_hex(const char *label, const unsigned char *data, size_t len) {
    printf("%s: ", label);
    for (size_t i = 0; i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main() {
    // Initialize OpenSSL
    OpenSSL_add_all_algorithms();
    ERR_load_crypto_strings();

    printf("AES-128-GCM (OpenSSL) Test\n");
    printf("==========================\n\n");

    // Test vectors
    unsigned char key[CRYPTO_KEYBYTES] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f
    };
    
    unsigned char nonce[CRYPTO_NPUBBYTES] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b
    };
    
    unsigned char plaintext[] = "Hello, World! This is a test message.";
    size_t plaintext_len = strlen((char *)plaintext);
    
    unsigned char ad[] = "Additional authenticated data";
    size_t ad_len = strlen((char *)ad);
    
    unsigned char ciphertext[1024];
    unsigned char decrypted[1024];
    unsigned long long ciphertext_len;
    unsigned long long decrypted_len;
    
    printf("Test 1: Basic encryption/decryption\n");
    printf("-----------------------------------\n");
    print_hex("Key", key, CRYPTO_KEYBYTES);
    print_hex("Nonce", nonce, CRYPTO_NPUBBYTES);
    printf("Plaintext: %s\n", plaintext);
    printf("AD: %s\n\n", ad);
    
    // Encrypt
    int result = crypto_aead_encrypt(ciphertext, &ciphertext_len,
                                   plaintext, plaintext_len,
                                   ad, ad_len,
                                   NULL, nonce, key);
    
    if (result != 0) {
        fprintf(stderr, "Encryption failed!\n");
        return 1;
    }
    
    printf("Encryption successful!\n");
    printf("Ciphertext length: %llu bytes (including %d-byte tag)\n", 
           ciphertext_len, CRYPTO_ABYTES);
    print_hex("Ciphertext + Tag", ciphertext, ciphertext_len);
    printf("\n");
    
    // Decrypt
    result = crypto_aead_decrypt(decrypted, &decrypted_len,
                               NULL,
                               ciphertext, ciphertext_len,
                               ad, ad_len,
                               nonce, key);
    
    if (result != 0) {
        fprintf(stderr, "Decryption failed!\n");
        return 1;
    }
    
    printf("Decryption successful!\n");
    printf("Decrypted length: %llu bytes\n", decrypted_len);
    decrypted[decrypted_len] = '\0';
    printf("Decrypted text: %s\n\n", decrypted);
    
    // Verify
    if (decrypted_len != plaintext_len || 
        memcmp(plaintext, decrypted, plaintext_len) != 0) {
        fprintf(stderr, "Decryption mismatch!\n");
        return 1;
    }
    
    printf("Test 2: Authentication failure test\n");
    printf("-----------------------------------\n");
    
    // Modify ciphertext
    ciphertext[0] ^= 0x01;
    
    result = crypto_aead_decrypt(decrypted, &decrypted_len,
                               NULL,
                               ciphertext, ciphertext_len,
                               ad, ad_len,
                               nonce, key);
    
    if (result == 0) {
        fprintf(stderr, "ERROR: Modified ciphertext was accepted!\n");
        return 1;
    }
    
    printf("Good: Modified ciphertext was rejected (authentication failed)\n\n");
    
    printf("Test 3: Empty plaintext\n");
    printf("-----------------------\n");
    
    result = crypto_aead_encrypt(ciphertext, &ciphertext_len,
                               NULL, 0,
                               ad, ad_len,
                               NULL, nonce, key);
    
    if (result != 0) {
        fprintf(stderr, "Encryption of empty plaintext failed!\n");
        return 1;
    }
    
    printf("Empty plaintext encrypted successfully\n");
    printf("Ciphertext length: %llu bytes (tag only)\n", ciphertext_len);
    
    result = crypto_aead_decrypt(decrypted, &decrypted_len,
                               NULL,
                               ciphertext, ciphertext_len,
                               ad, ad_len,
                               nonce, key);
    
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