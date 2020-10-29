# Adapted from https://en.wikipedia.org/wiki/User:Dantheox/flags.rb

def GetFlagEN(nation, year):
    if nation == "HOL":
        return "{{flagicon|NED}}"
    elif nation == "APA":
        return "{{flagicon|Czechoslovakia}}"
    elif nation == "AUT" and year <= 1918:
        return "{{flagicon|AUT|empire}}"
    elif nation == "BIH" and year <= 1998:
        return "{{flagicon|BIH|1992}}"
    elif nation == "BUL" and year <= 1971:
        return "{{flagicon|BUL|1967}}"
    elif nation == "BUL" and year <= 1990:
        return "{{flagicon|BUL|1971}}"
    elif nation == "CAN" and year <= 1920:
        return "{{flagicon|CAN|1868}}"
    elif nation == "CAN" and year <= 1964:
        return "{{flagicon|CAN|1921}}"
    elif nation == "CHN" and year <= 1949:
        return "{{flagicon|Republic of China|1912}}"
    elif nation == "EGY" and year < 1922:
        return "{{flagicon|EGY|1882}}"
    elif nation == "EGY" and year <= 1952:
        return "{{flagicon|EGY|1922}}"
    elif nation == "EGY" and year <= 1972:
        return "{{flagicon|EGY|1952}}"
    elif nation == "ESP" and year < 1931:
        return "{{flagicon|ESP|1785}}"
    elif nation == "ESP" and year < 1939:
        return "{{flagicon|ESP|1931}}"
    elif nation == "ESP" and year < 1977:
        return "{{flagicon|ESP|1939}}"
    elif nation == "ESP" and year < 1981:
        return "{{flagicon|ESP|1977}}"
    elif nation == "GEO" and year <= 2004:
        return "{{flagicon|GEO|1990}}"
    elif nation == "GER" and year <= 1918:
        return "{{flagicon|GER|empire}}"
    elif nation == "GER" and year <= 1934:
        return "{{flagicon|GER|Weimar}}"
    elif nation == "GER" and year <= 1945:
        return "{{flagicon|GER|Nazi}}"
    elif nation == "GRE" and year <= 1969:
        return "{{flagicon|GRE|old}}"
    elif nation == "HKG" and year <= 1997:
        return "{{flagicon|HKG|colonial}}"
    elif nation == "HUN" and year < 1940:
        return "{{flagicon|HUN|1867}}"
    elif nation == "HUN" and year <= 1945:
        return "{{flagicon|HUN|1920}}"
    elif nation == "HUN" and year <= 1956:
        return "{{flagicon|HUN|1949}}"
    elif nation == "IND" and year <= 1946:
        return "{{flagicon|IND|British}}"
    elif nation == "IRI" and year <= 1963:
        return "{{flagicon|IRI|1925}}"
    elif nation == "IRI" and year <= 1979:
        return "{{flagicon|IRI|1964}}"
    elif nation == "IRQ" and year < 1959:
        return "{{flagicon|IRQ|1924}}"
    elif nation == "IRQ" and year < 1963:
        return "{{flagicon|IRQ|1959}}"
    elif nation == "IRQ" and year < 1991:
        return "{{flagicon|IRQ|1963}}"
    elif nation == "IRQ" and year < 2003:
        return "{{flagicon|IRQ|1991}}"
    elif nation == "ITA" and year <= 1946:
        return "{{flagicon|ITA|1861}}"
    elif nation == "MAS" and year < 1948:
        return "{{flagicon|MAS|1895}}"
    elif nation == "MAS" and year <= 1963:
        return "{{flagicon|MAS|1948}}"
    elif nation == "MEX" and year <= 1933:
        return "{{flagicon|MEX|1916}}"
    elif nation == "MEX" and year <= 1968:
        return "{{flagicon|MEX|1934}}"
    elif nation == "RHO" and year <= 1967:
        return "{{flagicon|Rhodesia|1964}}"
    elif nation == "ROM" and year <= 1947:
        return "{{flagicon|ROM|1867}}"
    elif nation == "ROM" and year <= 1989:
        return "{{flagicon|ROM|1947}}"
    elif nation == "RSA" and year <= 1927:
        return "{{flagicon|RSA|1910}}"
    elif nation == "RSA" and year <= 1994:
        return "{{flagicon|RSA|1928}}"
    elif nation == "SRI" and year <= 1971:
        return "{{flagicon|SRI}}"
    elif nation == "VIE" and year <= 1974:
        return "{{flagicon|South Vietnam}}"
    elif nation == "YUG" and year <= 1941:
        return "{{flagicon|Kingdom of Yugoslavia}}"
    elif nation == "YUG" and year <= 2002:
        return "{{flagicon|FR Yugoslavia}}"
    elif nation == "" or nation == "ITF" or nation == "LAG":
        return ""
    else:
        return "{{flagicon|" + nation + "}}"
