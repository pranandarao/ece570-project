from Crypto.Cipher import AES
import os
import random
import struct
 
 
def decrypt_file(key, filename, origsize, chunk_size=64*1024):
    output_filename = os.path.splitext(filename)[0]
    with open(filename, 'rb') as infile:
        # origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        # iv = infile.read(16)
        # print('q:', struct.calcsize('Q'))
        decryptor = AES.new(key, AES.MODE_ECB)
        with open(output_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            # print(origsize)
            outfile.truncate(origsize)
 
 
def encrypt_file(key, filename, chunk_size=64*1024):
    output_filename = filename + '.encrypted'
    # iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    # encryptor = AES.new(key, AES.MODE_ECB, iv)
    encryptor = AES.new(key, AES.MODE_ECB)
    filesize = os.path.getsize(filename)
    with open(filename, 'rb') as inputfile:
        with open(output_filename, 'wb') as outputfile:
            # outputfile.write(struct.pack('<Q', filesize))
            # outputfile.write(iv)
            while True:
                chunk = inputfile.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outputfile.write(encryptor.encrypt(chunk))
    return filesize