def caesar_encrypt(text: str, shift: int,
                   alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:/?.@=") -> str:
    cipher_text = ""
    for char in text:
        if char in alphabet:
            index = alphabet.find(char)
            new_index = (index + shift) % len(alphabet)
            cipher_text += alphabet[new_index]

        else:
            cipher_text += char
    print(cipher_text)
    return cipher_text

# 加密明文
CON = caesar_encrypt("wICAveffByyDerEkxAvE:/?.i.dhdch/?:h??:e..:afCzsnoBgmrkBCoDjEDpcwl@", -10)