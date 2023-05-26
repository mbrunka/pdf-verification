import hashlib
from rsa import *
from wave import open as open_wave
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from os import listdir, path
from trng import trng_generate
from sympy import prevprime, nextprime
from random import randint


# TEST PURPOSES ONLY !!!!!!!!!!!!!!!!!!!!!!!!!!
SOUND_FILE_PATH = "data/sound-samples/test.wav"

KEYS_FOLDER = "keys"
PUBLIC_KEY_FILE = "public_key.pem"
PUBLIC_KEY_FILE_PATH = path.join(KEYS_FOLDER, PUBLIC_KEY_FILE)
PRIVATE_KEY_FILE = "private_key.pem"
PRIVATE_KEY_FILE_PATH = path.join(KEYS_FOLDER, PRIVATE_KEY_FILE)


print(PUBLIC_KEY_FILE_PATH)


def get_trng(sound_file_path):
    # Open the wave file and read the binary data
    w = open_wave(sound_file_path, "rb")
    if w is None:
        raise FileNotFoundError("Error: Unable to open file")
        exit()

    nframes = w.getnframes()
    # Read the audio data as a string of bytes
    audio_data = w.readframes(nframes)
    w.close()

    return trng_generate(audio_data)


def new_keys(sound_file):
    def gen_key_params(key_length=1024, e=65537):
        # Generate p and q values
        def generate_prime(random_ints):
            while True:
                index = randint(0, len(random_ints) - 1)
                num = random_ints[index]
                if num >= 128:
                    return num, index

        # list of random integers
        random_ints = get_trng(sound_file)

        p = 0
        q = 0

        for _ in range(key_length // 8):
            num, index = generate_prime(random_ints)
            p = (p << 8) + num
            random_ints.pop(index)

        for _ in range(key_length // 8):
            num, index = generate_prime(random_ints)
            q = (q << 8) + num
            random_ints.pop(index)

        # Make sure that p and q are prime numbers
        p = prevprime(p)
        q = nextprime(q)

        # Compute private exponent - d
        n = p * q
        phi_n = (p - 1) * (q - 1)
        d = pow(e, -1, phi_n)

        public_numbers = rsa.RSAPublicNumbers(e=e, n=n)
        private_numbers = rsa.RSAPrivateNumbers(
            p=p,
            q=q,
            d=d,
            dmp1=d % (p - 1),
            dmq1=d % (q - 1),
            iqmp=pow(q, -1, p),
            public_numbers=public_numbers,
        )

        private_key = private_numbers.private_key(default_backend())
        return private_key, private_key.public_key()

    private_numbers, public_numbers = gen_key_params(rdat)
    print("Keys has been generated")

    # Write public_key to file
    public_key_file = open(PUBLIC_KEY_FILE_PATH, "wb")
    public_key = public_numbers.public_key(default_backend())
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_key_file.write(public_key_pem)
    public_key_file.close()

    # Write private_key to file
    private_key_file = open(PRIVATE_KEY_FILE_PATH, "wb")
    private_key_pem = private_numbers.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_key_file.write(private_key_pem)
    private_key_file.close()

    return public_key, private_key


def get_private_numbers():
    try:
        f = open(PRIVATE_KEY_FILE_PATH, "rb")
        key_pem = f.read()
        f.close()
    except:
        raise FileNotFoundError("Error: private key not found")
        exit()

    private_key = serialization.load_pem_private_key(
        key_pem, password=None, backend=default_backend()
    )
    private_numbers = private_key.private_numbers()
    return private_numbers


def get_public_numbers():
    try:
        f = open(PUBLIC_KEY_FILE_PATH, "rb")
        key_pem = f.read()
        f.close()
    except:
        raise FileNotFoundError("Error: public key not found")
        exit()

    public_key = serialization.load_pem_public_key(key_pem, backend=default_backend())
    public_numbers = public_key.public_numbers()
    return public_numbers


def gen_hash(file_path):
    # Read the contents of the file
    with open(file_path, "rb") as file:
        content = file.read()

    # Generate the SHA-3 hash
    sha3_hash = hashlib.sha3_256(content).hexdigest()

    return sha3_hash


public_key, private_key = new_keys(SOUND_FILE_PATH)
hash_value = gen_hash()

# Generate RSA key pair
public_key, private_key = rsa.newkeys(2048)

# Encrypt the hash using the RSA private key
encrypted_hash = rsa.encrypt(hash_value.encode(), private_key)

# Decrypt the encrypted hash using the RSA private key
decrypted_hash = rsa.decrypt(encrypted_hash, private_key)

# Print or use the hash values as desired
print("Original Hash: ", hash_value)
print("Decrypted Hash: ", decrypted_hash)
