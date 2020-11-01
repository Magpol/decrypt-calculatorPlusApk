#!/usr/bin/env python
# Decrypt files from Calculator+ - https://github.com/Magpol
from Crypto.Cipher import DES
import argparse
import glob

key = b'12345678'
des = DES.new(key, DES.MODE_ECB)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Decrypt files from Android app eztools.calculator.photo.vault")
    parser.add_argument("--filedir", "-F", type=str,
                        required=True, help="Path to encrypted files")
    args = parser.parse_args()
    for afile in glob.glob(args.filedir+'/*'):
        print("Decrypting " + afile)
        file = open(afile,"rb")
        fileContent = file.read()
        try:        
            decryptedFileContent = des.decrypt(fileContent)
            decryptedFile = open(afile + '.decrypted','wb') # This line changed
            decryptedFile.write(decryptedFileContent)
            decryptedFile.close()
        except:
            print("## Error in decrypting file: " + afile)