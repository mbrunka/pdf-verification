import hashlib
import rsa
from get_trng import get_trng

# TEST PURPOSES ONLY !!!!!!!!!!!!!!!!!!!!!!!!!!
SOUND_FILE_PATH = "TRNG/sound-samples/test.wav"


# list of random integers
random_ints = get_trng(SOUND_FILE_PATH)

# Convert the list of random integers to a string
random_ints_str = " ".join(map(str, random_ints))

# Generate the SHA-3 hash of the random integers string
sha3_hash = hashlib.sha3_256()
sha3_hash.update(random_ints_str.encode())
hash_value = sha3_hash.hexdigest()

# Generate RSA key pair
public_key, private_key = rsa.newkeys(2048)

# Encrypt the hash using the RSA private key
encrypted_hash = rsa.encrypt(hash_value.encode(), private_key)

# Print or use the hash values as desired
print("Original Hash: ", hash_value)
print("Encrypted Hash: ", encrypted_hash)
print("Public Key: ", public_key)