G2_TAPS = {
    1: (2, 6),
    2: (3, 7),
    3: (4, 8),
    4: (5, 9),
    5: (1, 9),
    6: (2, 10),
    7: (1, 8),
    8: (2, 9),
    9: (3, 10),
    10: (2, 3),
    11: (3, 4),
    12: (5, 6),
    13: (6, 7),
    14: (7, 8),
    15: (8, 9),
    16: (9, 10),
    17: (1, 4),
    18: (2, 5),
    19: (3, 6),
    20: (4, 7),
    21: (5, 8),
    22: (6, 9),
    23: (1, 3),
    24: (4, 6),
    25: (5, 7),
    26: (6, 8),
    27: (7, 9),
    28: (8, 10),
    29: (1, 6),
    30: (2, 7),
    31: (3, 8),
    32: (4, 9),
}


def generate_ca_code_gps(prn):
    """
    Generate one period of the GPS L1 C/A code for a given PRN.

    Returns:
        List of 1023 binary chips, each chip being 0 or 1.
    """

    if prn not in G2_TAPS:
        raise ValueError("PRN must be between 1 and 32 for this table.")

    g1 = [1] * 10
    g2 = [1] * 10

    tap1, tap2 = G2_TAPS[prn]

    ca_code = []

    for _ in range(1023):
        # Output before shifting
        g1_out = g1[9]

        # PRN-specific G2 output …^ is the XOR of the two tap positions (modulo 2 addition)
        g2_out = g2[tap1 - 1] ^ g2[tap2 - 1]

        # C/A chip the first chip is before X0R??
        ca_chip = g1_out ^ g2_out
        ca_code.append(ca_chip)

        # Feedback bits 
        # For G1, the feedback is the XOR of bits 3 and 10 (0-indexed: 2 and 9)
        # For G2, the feedback is the XOR of bits 2, 3, 6, 8, 9, and 10 (0-indexed: 1, 2, 5, 7, 8, and 9)
        g1_feedback = g1[2] ^ g1[9]

        g2_feedback = (
            g2[1] ^ g2[2] ^ g2[5] ^
            g2[7] ^ g2[8] ^ g2[9]
        )

        # Shift right, insert feedback into stage 1
        g1 = [g1_feedback] + g1[:-1]
        g2 = [g2_feedback] + g2[:-1]

    return ca_code