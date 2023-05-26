import struct
import numpy as np


def trng_generate(audio_data, N=1024, L=8):
    """Generates true random numbers

    Args:
        audio_data (bytes): _description_
        N (int, optional): _description_. Defaults to 1024.
        L (int, optional): _description_. Defaults to 8.
    """

    def swap_bits(num):
        # Swap the 32 most significant bits with the 32 least significant bits
        msb = num >> 32
        lsb = num & ((1 << 32) - 1)
        swapped_num = (lsb << 32) | msb
        # Perform XOR operation to increase randomness
        result = swapped_num ^ num
        return result

    # Convert the audio data to a numpy array
    audio_data = np.frombuffer(audio_data, dtype=np.uint16)

    # given static
    GAMMA = 2
    EPSILON = 0.1
    ALPHA = 1
    n = int(N / 256 * 8)

    A = []
    for byte in audio_data:
        A.append(byte)

    # check if audio file is long enough
    if len(A) < n:
        raise ValueError("Audio file is too short")

    r = []
    mask = 0b00000111
    for v in A:
        r.append(v & mask)

    x = [
        [0.141592, 0.653589, 0.793238, 0.462643, 0.383279, 0.502884, 0.197169, 0.399375]
    ]

    def fT(x, ALPHA):
        if 0 <= x < 0.5:
            return ALPHA * x
        elif 0.5 <= x <= 1:
            return ALPHA * (1 - x)
        else:
            raise ValueError("x must be in range of [0, 1]")

    z = [0, 0, 0, 0, 0, 0, 0, 0]
    o = []
    y = 0

    while len(o) <= N:
        for i in range(L):
            t = len(x) - 1
            x[t][i] = ((0.071428571 * r[y]) + x[t][i]) * 0.666666667
        for t in range(GAMMA):
            for i in range(L):
                try:
                    x[t + 1][i] = (
                        (1 - EPSILON) * fT(x[t][i], ALPHA)
                        + EPSILON / 2 * (fT(x[t][(i + 1) % L], ALPHA))
                        + fT(x[t][(i - 1) % L], ALPHA)
                    )
                except:
                    x.append([0, 0, 0, 0, 0, 0, 0, 0])
                    x[t + 1][i] = (
                        (1 - EPSILON) * fT(x[t][i], ALPHA)
                        + EPSILON / 2 * (fT(x[t][(i + 1) % L], ALPHA))
                        + fT(x[t][(i - 1) % L], ALPHA)
                    )
        for i in range(L):
            word = struct.pack("d", x[2][i])
            # Konwersja ciągu bajtów na wartość uint64
            int_value = int.from_bytes(word, byteorder="big", signed=False)
            z[i] = int_value
            x[0][i] = x[2][i]
        for i in range(int(L / 2)):
            z[i] = int(z[i]) ^ swap_bits(int(z[i + int(L / 2)]))
        o.append(z[0] + z[1] * 256 + z[2] * pow(2, 16) + z[3] * pow(2, 24))
        y += 1

    # Pobieranie po 8 bitów z kazdej próbki wyjściowej
    bajty_z_O = []
    for j in range(len(o) - 1):
        for i in range(0, 256, 8):
            bajt = (o[j] >> (256 - (i + 8))) & 0xFF
            if bajt != 0:
                bajty_z_O.append(bajt)

    # print(len(bajty_z_O))
    return bajty_z_O
