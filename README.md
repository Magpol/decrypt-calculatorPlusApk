# Decrypting images hidden with **Calculator+**

**Calculator+ - Photo Vault & Video Vault hide photos** is an Android application that (description from Google Play store) "..looks like a beautiful calculator, and works very well, but have a secret photo vault behind it. all hide photos will be encrypted, uninstall the app will not delete the password, ".

The packagename is "eztools.calculator.photo.vault".

A user on the "Digital Forensics" discord asked if someone had a way of decrypting the images stored by the application. 

I had a weekend with some spare time so i analysed the application and found out how to decrypt the images. 

Here is how i did it:

## Step 1) Download the apk to your computer

### If you have the application installed on your phone: 

Connect the device to your computer, fire up a shell and grab it with adb:

````
c0mputer ~ % adb shell pm list packages|grep calc
package:eztools.calculator.photo.vault
c0mputer ~ % adb shell pm path eztools.calculator.photo.vault
package:/data/app/eztools.calculator.photo.vault-OP_MBoGMZN-LZ5wr50dNWA==/base.apk
c0mputer ~ % adb pull /data/app/eztools.calculator.photo.vault-OP_MBoGMZN-LZ5wr50dNWA==/base.apk
/data/app/eztools.calculator.photo.vault-OP_MBoGMZN-LZ5wr50dN...1 file pulled, 0 skipped. 17.7 MB/s (3185374 bytes in 0.171s)
````
Now the application is saved to "base.apk" and you can start to analyse it.

### If you want to download the apk from internet

Go to http://wwww.apkpure.com or http://www.apkmirror.com and search for the packagename "eztools.calculator.photo.vault". 
This is kinda important as Google playstore often have multiple applications, from different publishers, that share the same name and icon. You could end up with
the wrong apk if you dont pay attention.

## Step 2) Analyze the apk.

I loaded the apk into JADX-GUI, a tool that "produces Java source code from Android Dex and Apk files".

https://github.com/skylot/jadx

A very nice feature of jadx is that you can activate deobfuscation when parsing the apk. This will sometimes (often) do a pretty decent job of helping out with applications that are obfuscated when compiled.

Here the apk is loaded and deobfuscated:
![Loaded](/images/1.png "Loaded")

What i usually do next is to just click and look at all the classes and methods. I also use the search function to search for strings that should be of interest. In this case i searched for "encrypt", "decrypt", "AES" etc etc.

This looks interesting:
![Search](/images/2.png "Search")

So when i clicked the search result the following code showed up: 

````
FileInputStream fileInputStream = new FileInputStream(this.f6363e.f6361a);
ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
EncryptUtils.m10791a("12345678", fileInputStream, byteArrayOutputStream);
byteArrayOutputStream.flush();
ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArrayOutputStream.toByteArray());
this.f6362d = byteArrayInputStream;
aVar.mo2601d(byteArrayInputStream);
````

To view the method EncryptUtils.m10791a() you just right-click on it and select "Goto declaration".

![File](/images/3.png "File")

When looking at the Class and methods i saw that this was a class responsible for encrypting and decrypting files.

![Class](/images/4.png "Class") 

The creator of the app uses a static key "12345678" for encryption, and also uses "DES" encryption.

I wont comment further on the use of DES and a static key ;-). 

What we need to do is to find out where the files are stored, pull the files and then create something that will decrypt the files for us.

After following some code i ended up with this method:

````
    public static final String m18892g(Context context, String str, String str2) {
        File file;
        C3655i.m20371c(context, "context");
        C3655i.m20371c(str, "filePath");
        try {
            FileInputStream fileInputStream = new FileInputStream(new File(str));
            if (str2 == null) {
                file = new File(m18904s(context), m18895j());
            } else {
                file = new File(str2);
            }
            EncryptUtils.m10793c("12345678", fileInputStream, new FileOutputStream(file));
            return file.getAbsolutePath();
        } catch (IOException e) {
            C3435f.m18931d(e);
            return null;
        }
    }
````
new File(m18904s(context), m18895j()) seems to be of interest:

````
    public static final File m18904s(Context context) {
        C3655i.m20371c(context, "context");
        File externalFilesDir = context.getExternalFilesDir("photo_encrypt");
        if (externalFilesDir != null) {
            return externalFilesDir;
        }
        C3655i.m20376h();
        throw null;
    }
````
````
    public static final String m18895j() {
        String uuid = UUID.randomUUID().toString();
        C3655i.m20370b(uuid, "UUID.randomUUID().toString()");
        return uuid;
    }
````

The application is using files in "context.getExternalFilesDir" (https://developer.android.com/reference/android/content/Context#getExternalFilesDir) and the name seems to be a GUID. So lets see what we can find on our device:

````
c0mputer ~ % adb shell ls -la /storage/emulated/0/Android/data/eztools.calculator.photo.vault/files/photo_encrypt/
total 6180
drwxrwx--x 2 u0_a182 sdcard_rw    4096 2020-10-31 14:43 .
drwxrwx--x 3 u0_a182 sdcard_rw    4096 2020-10-31 14:43 ..
-rw-rw---- 1 u0_a182 sdcard_rw 4143408 2020-10-31 14:43 99fc748b-c096-4f90-82d8-5814428d2894
-rw-rw---- 1 u0_a182 sdcard_rw 2171184 2020-10-31 14:43 b7a93f1e-25af-4350-87f1-cec095062ff2
````

Bingo! Or?

## Step 3) Analyze and decrypt files.

Lets pull and view the files:

````
c0mputer ~ % adb pull /storage/emulated/0/Android/data/eztools.calculator.photo.vault/files/photo_encrypt/        
/storage/emulated/0/Android/data/eztools.calculator.photo.vau... 2 files pulled, 0 skipped. 16.8 MB/s (6314592 bytes in 0.358s)

c0mputer ~ % hexdump -C -n 80 99fc748b-c096-4f90-82d8-5814428d2894
00000000  a5 9f 94 39 5c 08 ec eb  83 87 87 51 d3 ce 3a 0a  |...9\......Q..:.|
00000010  84 9e 1e 85 2b 42 a9 b8  d4 74 ba d3 a6 87 af c2  |....+B...t......|
00000020  98 c5 04 86 57 6e bf 87  6d a7 c3 7d 1a a3 57 6f  |....Wn..m..}..Wo|
00000030  cf 73 e5 8f b8 c5 72 fd  9f 6f 2f 64 c4 51 ea 07  |.s....r..o/d.Q..|
00000040  8b 73 b9 63 1b f1 cb 40  f4 28 cb 81 1e c3 4a 28  |.s.c...@.(....J(|
````

The files are encrypted (doh!). So lets decrypt them!

I made a simple script based on what we saw when analysing the app in jadx:

- Static key "12345678"
- Des encryption.
- Filename is changed to a random guid.

If you want the correct filename you have to pull the db from /data/data/eztools.calculator.photo.vault/databases/cal.db (this requires a rooted device or a
full filesystem extraction). When looking at the create statement for the photo table we can see that it stores "src_photo_path":

````
CREATE TABLE `photo` (`_id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `name` TEXT, `bucket_name` TEXT, `src_photo_path` TEXT, `dest_photo_path` TEXT, `thumbnail_photo_path` TEXT, `folder_id` TEXT, `blob_name` TEXT, `download_url` TEXT, `deleted` INTEGER, `sync_status` INTEGER)
````

The script will decrypt all files in a provided path. 

````
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
````

Let's try it out:

````
c0mputer ~ % python3 decrypt.py -F files/photo_encrypt/
Decrypting files/photo_encrypt/99fc748b-c096-4f90-82d8-5814428d2894
Decrypting files/photo_encrypt/b7a93f1e-25af-4350-87f1-cec095062ff2
c0mputer ~ % file files/photo_encrypt/99fc748b-c096-4f90-82d8-5814428d2894.decrypted 
files/photo_encrypt/99fc748b-c096-4f90-82d8-5814428d2894.decrypted: JPEG image data, Exif standard: [TIFF image data, little-endian, direntries=10, manufacturer=samsung, model=SM-G930F, orientation=upper-right, xresolution=134, yresolution=142, resolutionunit=2, software=G930FXXU2ERE8, datetime=2020:10:31 14:43:55], baseline, precision 8, 4032x3024, components 3
````

There we have it. The files are decrypted.

## Step 4) Bruteforce the password

In some cases it may be of interest to bruteforce the password regardless of the encryption algorithm.
Luckily it is as easy as decrypting the files!
Take a second and look at this slightly refactored code from JADX:

![PersistPW](/images/5.png "PersistPW") 

We can see that the password is getting hashed as MD5. It's not salted. What a surprise!
Another surprise is that the implementation of converting MD5 digits to Hex-String is faulty.
But we will cover that in the script, just assume it's a real MD5, haha.
The MD5 hash is saved in two different locations, depending on your SDK.

For SDK >= 30 (Android 11) it's saved in shared preferences:
````
/data/data/eztools.calculator.photo.vault/shared_prefs/cal_settings.xml
````
Content:
````
<string name="vault_password">81dc9bdb52d04dc2036dbd8313ed055</string>
````

For everything else it's stored in a file located at:
````
/sdcard/.vault/password
````
It holds just the hash:
````
81dc9bdb52d04dc2036dbd8313ed055
````

Hint: The password has to be a 4 digit number without leading 0 (1000-9999).

Now just fire:
````
python3 bruteforce.py -H 81dc9bdb52d04dc2036dbd8313ed055
````
Within milliseconds you should get:
````
Found password: 1234
````

## Step 5) Final words

As SH said: “Be brave, be curious, be determined, overcome the odds. It can be done”. 

With all the (often free) tools and information easily available online everyone with a bit of forensic knowledge can do this kind of 
analysis. This application was a easy one, and many applications are just that. So get some tools and don't be scared to try some new things!  
  
