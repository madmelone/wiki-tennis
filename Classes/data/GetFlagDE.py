"""
Derived from:
 	wikiTT 2.8.3.001 by German-Wikipedia User: Mac6 Mac6v2 Mac6v3
	https://de.wikipedia.org/wiki/Benutzer:Siebenschläferchen/Flaggen by German-Wikipedia User: Siebenschläferchen
"""

import datetime

def GetFlagDE(nation, d):
	if nation == "BLR":
		d1 = datetime.date(1991, 9, 19)
		d2 = datetime.date(1995, 6, 7)
		d3 = datetime.date(2012, 2, 10)
		if d < d1:
			return "SUN"
		elif d >= d1 and d < d2:
			return "BLR-1991"
		elif d >= d2 and d < d3:
			return "BLR-1995"
	elif nation == "BRA":
		d1 = datetime.date(1960, 4, 14)
		d2 = datetime.date(1968, 5, 28)
		d3 = datetime.date(1992, 5, 12)
		if d < d1:
			return "BRA-1889"
		elif d >= d1 and d < d2:
			return "BRA-1960"
		elif d >= d2 and d < d3:
			return "BRA-1968"
	elif nation == "BUL":
		d1 = datetime.date(1990, 11, 27)
		if d.year >= 1948 and d.year < 1967:
			return "BGR-1948"
		elif d.year >= 1967 and d.year < 1971:
			return "BGR-1967"
		elif d.year >= 1971 and d < d1:
			return "BGR-1971"
		return "BGR"
	elif nation == "CRO":
		d1 = datetime.date(1990, 12, 22)
		if d < d1:
			return "YUG"
		return "HRV"
	elif nation == "CZE" or nation == "TCH" or nation == "SVK":
		d1 = datetime.date(1993, 1, 1)
		if d < d1:
			if nation == "CZE":
				return "CSK"
			elif nation == "TCH":
				return "CSK"
			elif nation == "SVK":
				return "CSK"
		else:
			if nation == "TCH":
				return "CZE"
	elif nation == "EGY":
		if d.year >= 1952 and d.year < 1958:
			return "EGY-1952"
		elif d.year >= 1958 and d.year < 1972:
			return "EGY-1958"
		elif d.year >= 1972 and d.year < 1984:
			return "EGY-1972"
	elif nation == "ESP":
		d1 = datetime.date(1981, 12, 19)
		if d.year >= 1938 and d.year < 1945:
			return "ESP-1938"
		if d.year >= 1945 and d.year < 1977:
			return "ESP-1945"
		elif d < d1:
			return "ESP-1977"
	elif nation == "GER" or nation == "FRG" or nation == "DDR":
		d1 = datetime.date(1919, 8, 14)
		d2 = datetime.date(1933, 3, 12)
		d3 = datetime.date(1935, 9, 15)
		d4 = datetime.date(1990, 10, 3)
		d5 = datetime.date(1949, 10, 7)
		d6 = datetime.date(1959, 10, 1)
		if nation != "DDR":
			if d >= d1 and d < d2:
				return "DEU-1919"
			elif d >= d2 and d < d3:
				return "DEU-1933"
			elif d >= d3 and d.year < 1949:
				return "DEU-1935"
			elif d.year >= 1949 and d < d4:
				return "DEU-1949"
			elif d >= d4:
				return "DEU"
		else:
			if d >= d5 and d < d6:
				return "GDR-1949"
			if d >= d6:
				return "GDR"
	elif nation == "GEO":
		d1 = datetime.date(1991, 9, 4)
		d2 = datetime.date(2004, 1, 26)
		if d < d1:
			return "SUN-1980"
		elif d >= d1 and d < d2:
			return "GEO-1990"
	elif nation == "GRE":
		d1 = datetime.date(1970, 8, 18)
		d2 = datetime.date(1975, 6, 1)
		d3 = datetime.date(1978, 12, 22)
		if d.year >= 1935 and d < d1:
			return "GRC-1935"
		elif d >= d1 and d < d2:
			return "GRC-1970"
		elif d >= d2 and d < d3:
			return "GRC-1975"
		return "GRC"
	elif nation == "HKG":
		d1 = datetime.date(1997, 7, 1)
		if d.year >= 1959 and d < d1:
			return "HKG-1959"
		return "CN-HK"
	elif nation == "HUN":
		if d.year >= 1957 and d.year < 1988:
			return "HUN-1957"
	elif nation == "IRN":
		d1 = datetime.date(1980, 7, 29)
		if d.year > 1964 and d < d1:
			return "IRN-1964"
	elif nation == "LAT":
		d1 = datetime.date(1990, 2, 27)
		if d < d1:
			return "SUN-1980"
		return "LVA"
	elif nation == "PAR":
		if d.year >= 1954 and d.year < 1988:
			return "PRY-1954"
		elif d.year >= 1988 and d.year < 1990:
			return "PRY-1988"
		elif d.year >= 1990 and d.year < 2013:
			return "PRY-1990"
		return "PRY"
	elif nation == "PHI":
		if d.year >= 1944 and d.year < 1981:
			return "PHL-1944"
		elif d.year >= 1981 and d.year < 1986:
			return "PHL-1981"
		elif d.year >= 1986 and d.year < 1990:
			return "PHL-1986"
		return "PHL"
	elif nation == "ROU":
		d1 = datetime.date(1952, 9, 25)
		d2 = datetime.date(1965, 8, 22)
		d3 = datetime.date(1989, 12, 27)
		if d >= d1 and d < d2:
			return "ROU-1952"
		elif d >= d2 and d < d3:
			return "ROU-1965"
	elif nation == "RSA":
		d1 = datetime.date(1994, 4, 27)
		if d.year >= 1928 and d.year < 1961:
			return "ZAF-1928"
		elif d.year >= 1961 and d < d1:
			return "ZAF-1961"
		return "ZAF"
	elif nation == "SLO":
		d1 = datetime.date(1991, 6, 27)
		if d < d1:
			return "YUG"
		return "SVN"
	elif nation == "SRB":
		d1 = datetime.date(1992, 4, 27)
		d2 = datetime.date(2003, 2, 4)
		d3 = datetime.date(2006, 6, 3)
		d4 = datetime.date(2010, 11, 11)
		if d >= d1 and d < d2:
			return "YUG-1992"
		elif d >= d2 and d < d3:
			return "SCG"
		elif d >= d3 and d < d4:
			return "SRB-2004"
	elif nation == "UKR":
		d1 = datetime.date(1991, 9, 4)
		if d < d1:
			return "SUN-1980"
	elif nation == "URS" or nation == "RUS":
		d1 = datetime.date(1980, 8, 15)
		d2 = datetime.date(1991, 8, 22)
		d3 = datetime.date(1993, 12, 11)
		if d.year >= 1955 and d < d1:
			return "SUN-1955"
		elif d >= d1 and d < d2:
			return "SUN"
		elif d >= d2 and d < d3:
			return "RUS-1991"
		#"URS" return "LVA" // 1992 an bei Savchenko
		#"URS" return "EUN" "GEO" return "EUN" "BLR" return "EUN" // Vereintes Team
	elif nation == "VEN":
		d1 = datetime.date(2006, 3, 12)
		if d.year > 1954 and d < d1:
			return "VEN-1954"
	elif nation == "YUG":
		d1 = datetime.date(1946, 1, 31)
		d2 = datetime.date(1992, 4, 27)
		d3 = datetime.date(2003, 2, 4)
		d4 = datetime.date(2006, 6, 3)
		if d >= d1 and d < d2:
			return "YUG-1946"
		elif d >= d2 and d < d3:
			return "YUG-1992"
		elif d >= d3 and d < d4:
			return "SCG"
	elif nation == "NED":
		return "NLD"
	elif nation == "URU":
		return "URY"
	elif nation == "SUI":
		return "CHE"
	elif nation == "ZIM":
		return "ZWE"
	elif nation == "DEN":
		return "DNK"
	elif nation == "OMA":
		return "OMN"
	elif nation == "CIS":
		return "GUS"
	elif nation == "INA":
		return "IDN"
	elif nation == "POR":
		return "PRT"
	elif nation == "CHI":
		return "CHL"
	elif nation == "MAD":
		return "MDG"
	elif nation == "CRC":
		return "CRI"
	elif nation == "PUR":
		return "US-PR"
	elif nation == "BAH":
		return "BHS"
	elif nation == "ALG":
		return "DZA"
	elif nation == "CAM":
		return "KHM"
	elif nation == "UAE":
		return "ARE"
	elif nation == "LIB":
		return "LBN"
	elif nation == "TOG":
		return "TGO"
	elif nation == "AHO":
		return "ANT"
	elif nation == "TWN":
		return "TPE"
	elif nation == "ESA":
		return "SLV"
	elif nation == "KUW":
		return "KWT"
	elif nation == "BAR":
		return "BRB"
	elif nation == "ANG":
		return "AGO"
	elif nation == "HAI":
		return "HTI"
	elif nation == "MON":
		return "MCO"
	elif nation == "MAS":
		return "MYS"
	elif nation == "GUA":
		return "GTM"
	elif nation == "VIE":
		return "VNM"
	elif nation == "NGR":
		return "NGA"
	return nation
