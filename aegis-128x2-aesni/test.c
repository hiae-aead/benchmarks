#include <stdio.h>
#include <stdint.h>
#include "crypto_aead.h"

int main(void) {
    printf("AEGIS-128x2 Intel AES-NI implementation compiled successfully!\n");
    printf("Key bytes: %d\n", CRYPTO_KEYBYTES);
    printf("Nonce bytes: %d\n", CRYPTO_NPUBBYTES);
    printf("Auth bytes: %d\n", CRYPTO_ABYTES);
    return 0;
}