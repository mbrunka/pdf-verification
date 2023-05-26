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

DATA_FOLDER = "data"
KEYS_FOLDER = "keys"
SIGN_FOLDER = "signatures"

PUBLIC_KEY_FILE = "public_key.pem"
PUBLIC_KEY_FILE_PATH = path.join(DATA_FOLDER, KEYS_FOLDER, PUBLIC_KEY_FILE)

PRIVATE_KEY_FILE = "private_key.pem"
PRIVATE_KEY_FILE_PATH = path.join(DATA_FOLDER, KEYS_FOLDER, PRIVATE_KEY_FILE)


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
    def generate_prime(random_ints):
        while True:
            num = random_ints.pop(randint(0, len(random_ints) - 1))
            if num >= 128:
                return num

    # Generate p and q values
    random_ints = get_trng(sound_file)
    KEY_LENGTH = 1024
    E = 65537

    p = 0
    q = 0

    for _ in range(KEY_LENGTH // 8):
        p = (p << 8) + generate_prime(random_ints)

    for _ in range(KEY_LENGTH // 8):
        q = (q << 8) + generate_prime(random_ints)

    # Make sure that p and q are prime numbers
    p = prevprime(p)
    q = nextprime(q)

    # Compute private exponent - d
    n = p * q
    phi_n = (p - 1) * (q - 1)
    d = pow(E, -1, phi_n)

    public_numbers = rsa.RSAPublicNumbers(e=E, n=n)
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
    print("Keys have been generated")

    # Write public_key to file
    public_key = public_numbers.public_key(default_backend())
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(PUBLIC_KEY_FILE_PATH, "wb") as public_key_file:
        public_key_file.write(public_key_pem)

    # Write private_key to file
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(PRIVATE_KEY_FILE_PATH, "wb") as private_key_file:
        private_key_file.write(private_key_pem)


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
    sha3_hash = hashlib.sha3_256(content).digest()

    return sha3_hash


# ------------------------------------------------------
def sign_file(pdf_file_path):
    # Get file hash
    print("Signing file: " + pdf_file_path)
    hash_value = gen_hash(pdf_file_path)

    # get private key
    private_key = get_private_numbers().private_key(default_backend())
    print("Private key has been loaded")
    # Sign the file hash
    signature = private_key.sign(hash_value, padding.PKCS1v15(), hashes.SHA3_256())
    print("signature has been generated")

    # Write signature to .dat file
    sign_file_path = "data/signatures/sign.dat"
    with open(sign_file_path, "wb") as sign_file:
        sign_file.write(signature)
    print("File has been signed")


def check_signature(signature_file_path, pdf_file_path, public_key_path):
    if not path.exists(signature_file_path):
        print("Error: signature file not found")
        exit()
    with open(signature_file_path, "rb") as signature_file:
        signature = signature_file.read()

    public_key = get_public_numbers().public_key(default_backend())

    # Calculate hash of the file
    file_hash = gen_hash(pdf_file_path)

    # Verify the signature
    try:
        public_key.verify(signature, file_hash, padding.PKCS1v15(), hashes.SHA3_256())
        print("Signature is valid.")
    except InvalidSignature:
        print("Signature is invalid.")
