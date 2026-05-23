def to_float(s):
    """convert numbers in RINEX  to float format, e.g. 1.234567D-08 -> 1.234567e-08"""
    s = s.strip().replace("D", "E")
    return float(s) if s else None


def to_int(s):
    s = s.strip()
    return int(float(s)) if s else None


def read_nav(filename):
    SV = {}

    with open(filename, "r") as file:
        # 1. 跳过 header，直到 END OF HEADER
        for line in file:
            if "END OF HEADER" in line:
                break

        # 2. 逐块读取导航数据
        while True:
            line = file.readline()
            if not line:
                break

            if len(line.strip()) == 0:
                continue

            sv = to_int(line[1:3])

            if sv not in SV:
                SV[sv] = {}

            navData = {}

            # 第一行
            navData["year"] = to_int(line[4:8])
            navData["month"] = to_int(line[8:11])
            navData["day"] = to_int(line[11:14])
            navData["hour"] = to_int(line[14:17])
            navData["minute"] = to_int(line[17:20])
            navData["second"] = to_int(line[20:23])

            navData["af0"] = to_float(line[23:43])
            navData["af1"] = to_float(line[43:62])
            navData["af2"] = to_float(line[62:81])

            # 第二行
            line = file.readline()
            navData["IODE"] = to_float(line[5:24])
            navData["Crs"] = to_float(line[24:43])
            navData["DeltaN"] = to_float(line[43:62])
            navData["M0"] = to_float(line[62:81])

            # 第三行
            line = file.readline()
            navData["Cuc"] = to_float(line[5:24])
            navData["e"] = to_float(line[24:43])
            navData["Cus"] = to_float(line[43:62])
            navData["sqrtA"] = to_float(line[62:81])

            # 第四行
            line = file.readline()
            navData["TOE"] = to_float(line[5:24])
            navData["Cic"] = to_float(line[24:43])
            navData["OMEGA0"] = to_float(line[43:62])
            navData["Cis"] = to_float(line[62:81])

            # 第五行
            line = file.readline()
            navData["i0"] = to_float(line[5:24])
            navData["Crc"] = to_float(line[24:43])
            navData["omega"] = to_float(line[43:62])
            navData["OMEGA_DOT"] = to_float(line[62:81])

            # 第六行
            line = file.readline()
            navData["IDOT"] = to_float(line[5:24])
            navData["CodesOnL2Channel"] = to_float(line[24:43])
            navData["GPSWeek"] = to_float(line[43:62])
            navData["GPSWeek2"] = to_float(line[62:81])

            # 第七行
            line = file.readline()
            navData["SVaccuracy"] = to_float(line[5:24])
            navData["SVhealth"] = to_float(line[24:43])
            navData["TGD"] = to_float(line[43:62])
            navData["IODCIssueOfData"] = to_float(line[62:81])

            # 第八行
            line = file.readline()
            navData["TransmissionTimeOfMessage"] = to_float(line[5:24])

            SV[sv]["navData"] = navData

    return SV