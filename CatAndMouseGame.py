import base64
import py3rijndael
import gzip
import msgpack
import main

def get_asset_bundle(asset_bundle_base64):
    try:
        # Base64 decode the asset bundle
        decoded_data = base64.b64decode(asset_bundle_base64)
        
        # Default key (for NA)
        key = b'nn33CYId2J1ggv0bYDMbYuZ60m4GZt5P'
        
        # Extract IV (first 32 bytes) and encrypted data
        iv = decoded_data[:32]
        encrypted_data = decoded_data[32:]

        # Select key based on region
        if main.fate_region == "JP":
            key = b'W0Juh4cFJSYPkebJB9WpswNF51oa6Gm7'
        
        # Initialize the Rijndael cipher
        cipher = py3rijndael.RijndaelCbc(
            key,
            iv,
            py3rijndael.paddings.Pkcs7Padding(16),
            32
        )

        # Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Decompress the decrypted data
        decompressed_data = gzip.decompress(decrypted_data)
        
        # Unpack the decompressed data
        unpacked_data = msgpack.unpackb(decompressed_data)

        return unpacked_data

    except (base64.binascii.Error, py3rijndael.DecryptionError, gzip.BadGzipFile, msgpack.ExtraData) as e:
        print(f"An error occurred: {e}")
        return None