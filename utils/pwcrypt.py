from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from get2unix.settings import TOKEN, SECRET_KEY


class EncryptStr(object):
    def __init__(self):
        self.key = TOKEN
        self.mode = AES.MODE_CBC

    def encrypt(self, username, password):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        text = SECRET_KEY + username + SECRET_KEY + password + SECRET_KEY
        count = len(text)
        if (count % length != 0):
            add = length - (count % length)
        else:
            add = 0
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    # 解密后，补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        raw = plain_text.decode('utf-8').strip('\0')
        return raw.split(SECRET_KEY)[1:3]