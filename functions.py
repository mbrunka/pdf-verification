import hashlib
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from wave import open as open_wave
from trng import trng_generate
from sympy import prevprime, nextprime
from random import randint

# Paths and folders
DATA_FOLDER = "data"
KEYS_FOLDER = "keys"
SIGN_FOLDER = "signatures"

PUBLIC_KEY_FILE = "public_key.pem"
PUBLIC_KEY_FILE_PATH = os.path.join(DATA_FOLDER, KEYS_FOLDER, PUBLIC_KEY_FILE)

# Sound file path (for test purposes only)
SOUND_FILE_PATH = "data/sound-samples/test.wav"


def get_trng(sound_file_path):
    """
    Generate random numbers using True Random Number Generator (TRNG).

    Args:
        sound_file_path (str): Path to the sound file.

    Returns:
        list: List of random integers generated from the sound file.
    """
    # Open the wave file and read the binary data
    w = open_wave(sound_file_path, "rb")
    if w is None:
        raise FileNotFoundError("Error: Unable to open file")

    nframes = w.getnframes()
    # Read the audio data as a string of bytes
    audio_data = w.readframes(nframes)
    w.close()

    return trng_generate(audio_data)


def new_keys(sound_file):
    """
    Generate new RSA key pair and save public key to file and return private key.

    Args:
        sound_file (str): Path to the sound file for generating random numbers.

    Returns:
        private_key (cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey): Private key.
    """

    # Generate p and q values
    random_ints = get_trng(sound_file)
    KEY_LENGTH = 512
    E = 65537

    p = 0
    q = 0

    for _ in range(KEY_LENGTH // 8):
        p = (p << 8) + random_ints.pop()

    for _ in range(KEY_LENGTH // 8):
        q = (q << 8) + random_ints.pop()

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

    # return private_key for function sign_file
    return private_key


def get_public_numbers(public_key_file=PUBLIC_KEY_FILE_PATH):
    """
    Retrieve the public key numbers from the public key file.

    Returns:
        RSAPublicNumbers: Public key numbers.
    """
    try:
        with open(public_key_file, "rb") as f:
            key_pem = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("Error: public key not found")

    public_key = serialization.load_pem_public_key(key_pem, backend=default_backend())
    public_numbers = public_key.public_numbers()
    return public_numbers


def gen_hash(file_path):
    """
    Generate the SHA-3 hash of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        bytes: SHA-3 hash value.
    """
    # Read the contents of the file
    with open(file_path, "rb") as file:
        content = file.read()

    # Generate the SHA-3 hash
    sha3_hash = hashlib.sha3_256(content).digest()

    return sha3_hash


def sign_file(pdf_file_path, private_key):
    """
    Sign a PDF file using RSA private key.

    Args:
        pdf_file_path (str): Path to the PDF file.
        private_key (RSAPrivateKey): RSA private key. Generated from new_keys function.
    """
    # Get file hash
    hash_value = gen_hash(pdf_file_path)

    # Get private key
    # private_key = private_key.private_key(default_backend())

    # Sign the file hash
    signature = private_key.sign(hash_value, padding.PKCS1v15(), hashes.SHA3_256())

    # Write signature to .dat file
    sign_file_path = os.path.join(DATA_FOLDER, SIGN_FOLDER, "sign.dat")
    with open(sign_file_path, "wb") as sign_file:
        sign_file.write(signature)
    return True, [sign_file_path, PUBLIC_KEY_FILE_PATH]


def check_signature(signature_file_path, pdf_file_path, public_key_path):
    """
    Check the signature of a PDF file using RSA public key.

    Args:
        signature_file_path (str): Path to the signature file.
        pdf_file_path (str): Path to the PDF file.
        public_key_path (str): Path to the public key file.
    """
    if not os.path.exists(signature_file_path):
        print("Error: signature file not found")
        return

    with open(signature_file_path, "rb") as signature_file:
        signature = signature_file.read()

    public_key = get_public_numbers(public_key_path).public_key(default_backend())

    # Calculate hash of the file
    file_hash = gen_hash(pdf_file_path)

    # Verify the signature
    try:
        public_key.verify(signature, file_hash, padding.PKCS1v15(), hashes.SHA3_256())
        return True
    except InvalidSignature:
        return False
