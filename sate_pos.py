import numpy as np

# GPS constants
GM = 3.986005e14                 # Earth's universal gravitational parameter, m^3/s^2
OmegaEDot = 7.2921151467e-5      # Earth rotation rate, rad/s
FULL_WEEK = 604800.0
HALF_WEEK = 302400.0


def check_gps_time(tk):
    """
    Correct GPS week crossover.
    tk should be in seconds.
    """
    if tk > HALF_WEEK:
        tk -= FULL_WEEK
    elif tk < -HALF_WEEK:
        tk += FULL_WEEK
    return tk


def solve_kepler(M, e, tol=1e-13, max_iter=30):
    """
    Solve Kepler equation:
        M = E - e sin(E)

    Returns eccentric anomaly E.
    """
    E = M

    for _ in range(max_iter):
        E_new = M + e * np.sin(E)

        if abs(E_new - E) < tol:
            break
        E = E_new
    return E


def sate_pos_ap1(t, eph):
    """
    Compute satellite ECEF position from broadcast ephemeris.

    Parameters
    ----------
    t : float
        Signal transmission time in GNSS system time, seconds of week.
        For GPS, this should be GPS seconds of week.

    eph : dict
        Broadcast ephemeris parameters from RINEX nav file.

        Required keys:
            sqrtA       : square root of semi-major axis
            e           : eccentricity
            M0          : mean anomaly at reference time
            DeltaN      : correction to mean motion
            toe         : time of ephemeris
            omega       : argument of perigee, small omega
            Cuc, Cus    : latitude correction terms
            Crc, Crs    : radius correction terms
            Cic, Cis    : inclination correction terms
            i0          : inclination at reference time
            IDOT        : rate of inclination
            OMEGA0      : longitude of ascending node
            OMEGADot    : rate of right ascension

    Returns
    -------
    X, Y, Z : float
        Satellite ECEF coordinates in meters.
    """

    # -----------------------------
    # 1. Read parameters
    # -----------------------------
    sqrtA = eph["sqrtA"]
    e = eph["e"]
    M0 = eph["M0"]
    DeltaN = eph["DeltaN"]
    toe = eph["TOE"]

    omega = eph["omega"]          # small omega: argument of perigee
    Cuc = eph["Cuc"]
    Cus = eph["Cus"]
    Crc = eph["Crc"]
    Crs = eph["Crs"]
    Cic = eph["Cic"]
    Cis = eph["Cis"]

    i0 = eph["i0"]
    IDOT = eph["IDOT"]

    OMEGA0 = eph["OMEGA0"]        # capital Omega
    OMEGADot = eph["OMEGA_DOT"]

    # -----------------------------
    # 2. Time from ephemeris reference epoch
    # -----------------------------
    tk = t - toe
    tk = check_gps_time(tk)

    # -----------------------------
    # 3. Semi-major axis
    # -----------------------------
    A = sqrtA ** 2

    # -----------------------------
    # 4. Mean motion
    # -----------------------------
    n0 = np.sqrt(GM / A**3)
    n = n0 + DeltaN

    # -----------------------------
    # 5. Mean anomaly
    # -----------------------------
    M = M0 + n * tk

    # -----------------------------
    # 6. Eccentric anomaly
    # -----------------------------
    E = solve_kepler(M, e)

    # -----------------------------
    # 7. True anomaly
    # #v = np.arctan2(
    #    np.sqrt(1 - e**2) * np.sin(E),
    #   np.cos(E) - e
    v = 2 * np.arctan2(
        np.sqrt(1 + e) * np.sin(E / 2),
        np.sqrt(1 - e) * np.cos(E / 2)
    )
    # -----------------------------
    # 8. Argument of latitude before correction
    # -----------------------------
    phi = v + omega

    # -----------------------------
    # 9. Second harmonic corrections
    # -----------------------------
    du = Cuc * np.cos(2 * phi) + Cus * np.sin(2 * phi)
    dr = Crc * np.cos(2 * phi) + Crs * np.sin(2 * phi)
    di = Cic * np.cos(2 * phi) + Cis * np.sin(2 * phi)

    # Corrected argument of latitude
    u = phi + du

    # Corrected radius
    r = A * (1 - e * np.cos(E)) + dr

    # Corrected inclination
    i = i0 + IDOT * tk + di

    # -----------------------------
    # 10. Position in orbital plane
    # -----------------------------
    x_orb = r * np.cos(u)
    y_orb = r * np.sin(u)

    # -----------------------------
    # 11. Corrected longitude of ascending node
    # -----------------------------
    OMEGA = OMEGA0 + (OMEGADot - OmegaEDot) * tk - OmegaEDot * toe

    # -----------------------------
    # 12. Convert to ECEF coordinates
    # -----------------------------
    X = x_orb * np.cos(OMEGA) - y_orb * np.cos(i) * np.sin(OMEGA)
    Y = x_orb * np.sin(OMEGA) + y_orb * np.cos(i) * np.cos(OMEGA)
    Z = y_orb * np.sin(i) 
    
    # velocity components (not required for position, but useful for completeness)
    Vx = -x_orb * np.sin(OMEGA) * OMEGADot + y_orb * np.cos(OMEGA) * OMEGADot * np.cos(i) + y_orb * np.sin(OMEGA) * IDOT * np.cos(i)
    Vy = x_orb * np.cos(OMEGA) * OMEGADot + y_orb * np.sin(OMEGA) * OMEGADot * np.cos(i) - y_orb * np.cos(OMEGA) * IDOT * np.cos(i)
    Vz = y_orb * np.cos(i) * IDOT

    return X, Y, Z