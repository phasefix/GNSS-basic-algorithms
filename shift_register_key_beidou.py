# phase assignment for Beidou G2 for L1 C/A code generation
G2_TAPS = {
    1: (1, 3),
    2: (1, 4),
    3: (1, 5),
    4: (1, 6),
    5: (1, 8),
    6: (1, 9),
    7: (1, 10),
    8: (1, 11),
    9: (2, 7),
    10: (3, 4),
    11: (3, 5),
    12: (3, 6),
    13: (3, 8),
    14: (3, 9),
    15: (3, 10),
    16: (3, 11),
    17: (4, 5),
    18: (4, 6),
    19: (4, 8),
    20: (4, 9),
    21: (4, 10),
    22: (4, 11),
    23: (5, 6),
    24: (5, 8),
    25: (5, 9),
    26: (5, 10),
    27: (5, 11),
    28: (6, 8),
    29: (6, 9),
    30: (6, 10),
    31: (6, 11),
    32: (8, 9),
}


def generate_ca_code_beidou(prn):
    """
    Generate one period of the Beidou L1 C/A code for a given PRN.

    Returns:
        List of 1023 binary chips, each chip being 0 or 1.
    """

    if prn not in G2_TAPS:
        raise ValueError("PRN must be between 1 and 32 for this table.")

    g1 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # G1 has a period of 2046 chips, so we need 11 stages
    g2 = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0] # G2 also has a period of 2046 chips

    tap1, tap2 = G2_TAPS[prn]

    ca_code = []

    for _ in range(2046):  # Beidou L1 C/A code has a period of 2046 chips
        # Output before shifting
        g1_out = g1[10]

        # PRN-specific G2 output …^ is the XOR of the two tap positions (modulo 2 addition)
        g2_out = g2[tap1 - 1] ^ g2[tap2 - 1]

        # C/A chip the first chip is before X0R??
        ca_chip = g1_out ^ g2_out
        ca_code.append(ca_chip)

        # Feedback bits 
        # For G1, the feedback is the XOR of bits 3 and 10 (0-indexed: 2 and 9)
        # For G2, the feedback is the XOR of bits 2, 3, 6, 8, 9, and 10 (0-indexed: 1, 2, 5, 7, 8, and 9)
        g1_feedback = g1[0] ^ g1[6] ^ g1[7] ^ g1[8] ^ g1[9] ^ g1[10]

        g2_feedback = (
            g2[0] ^ g2[1] ^ g2[2] ^
            g2[3] ^ g2[4] ^ g2[7] ^ g2[8] ^ g2[10]
        )

        # Shift right, insert feedback into stage 1
        g1 = [g1_feedback] + g1[:-1]
        g2 = [g2_feedback] + g2[:-1]

    return ca_code