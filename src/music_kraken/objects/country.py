from __future__ import annotations

from dataclasses import dataclass

import pycountry


CountryTyping = type(list(pycountry.countries)[0])


emoji_map = {'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬', 'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴', 'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹', 'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿', 'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪', 'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮', 'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳', 'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸', 'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾', 'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩', 'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮', 'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳', 'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻', 'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿', 'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲', 'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪', 'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸', 'ET': '🇪🇹', 'FI': '🇫🇮', 'FJ': '🇫🇯', 'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷', 'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪', 'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮', 'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵', 'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹', 'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰', 'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹', 'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱', 'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶', 'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪', 'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪', 'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲', 'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼', 'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧', 'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷', 'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻', 'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩', 'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭', 'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳', 'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷', 'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻', 'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿', 'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫', 'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴', 'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿', 'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫', 'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱', 'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸', 'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦', 'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺', 'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨', 'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭', 'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱', 'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷', 'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽', 'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩', 'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯', 'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳', 'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻', 'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬', 'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿', 'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬', 'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫', 'WS': '🇼🇸', 'YE': '🇾🇪', 'YT': '🇾🇹', 'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼', '🇦🇩': 'AD', '🇦🇪': 'AE', '🇦🇫': 'AF', '🇦🇬': 'AG', '🇦🇮': 'AI', '🇦🇱': 'AL', '🇦🇲': 'AM', '🇦🇴': 'AO', '🇦🇶': 'AQ', '🇦🇷': 'AR', '🇦🇸': 'AS', '🇦🇹': 'AT', '🇦🇺': 'AU', '🇦🇼': 'AW', '🇦🇽': 'AX', '🇦🇿': 'AZ', '🇧🇦': 'BA', '🇧🇧': 'BB', '🇧🇩': 'BD', '🇧🇪': 'BE', '🇧🇫': 'BF', '🇧🇬': 'BG', '🇧🇭': 'BH', '🇧🇮': 'BI', '🇧🇯': 'BJ', '🇧🇱': 'BL', '🇧🇲': 'BM', '🇧🇳': 'BN', '🇧🇴': 'BO', '🇧🇶': 'BQ', '🇧🇷': 'BR', '🇧🇸': 'BS', '🇧🇹': 'BT', '🇧🇻': 'BV', '🇧🇼': 'BW', '🇧🇾': 'BY', '🇧🇿': 'BZ', '🇨🇦': 'CA', '🇨🇨': 'CC', '🇨🇩': 'CD', '🇨🇫': 'CF', '🇨🇬': 'CG', '🇨🇭': 'CH', '🇨🇮': 'CI', '🇨🇰': 'CK', '🇨🇱': 'CL', '🇨🇲': 'CM', '🇨🇳': 'CN', '🇨🇴': 'CO', '🇨🇷': 'CR', '🇨🇺': 'CU', '🇨🇻': 'CV', '🇨🇼': 'CW', '🇨🇽': 'CX', '🇨🇾': 'CY', '🇨🇿': 'CZ', '🇩🇪': 'DE', '🇩🇯': 'DJ', '🇩🇰': 'DK', '🇩🇲': 'DM', '🇩🇴': 'DO', '🇩🇿': 'DZ', '🇪🇨': 'EC', '🇪🇪': 'EE', '🇪🇬': 'EG', '🇪🇭': 'EH', '🇪🇷': 'ER', '🇪🇸': 'ES', '🇪🇹': 'ET', '🇫🇮': 'FI', '🇫🇯': 'FJ', '🇫🇰': 'FK', '🇫🇲': 'FM', '🇫🇴': 'FO', '🇫🇷': 'FR', '🇬🇦': 'GA', '🇬🇧': 'GB', '🇬🇩': 'GD', '🇬🇪': 'GE', '🇬🇫': 'GF', '🇬🇬': 'GG', '🇬🇭': 'GH', '🇬🇮': 'GI', '🇬🇱': 'GL', '🇬🇲': 'GM', '🇬🇳': 'GN', '🇬🇵': 'GP', '🇬🇶': 'GQ', '🇬🇷': 'GR', '🇬🇸': 'GS', '🇬🇹': 'GT', '🇬🇺': 'GU', '🇬🇼': 'GW', '🇬🇾': 'GY', '🇭🇰': 'HK', '🇭🇲': 'HM', '🇭🇳': 'HN', '🇭🇷': 'HR', '🇭🇹': 'HT', '🇭🇺': 'HU', '🇮🇩': 'ID', '🇮🇪': 'IE', '🇮🇱': 'IL', '🇮🇲': 'IM', '🇮🇳': 'IN', '🇮🇴': 'IO', '🇮🇶': 'IQ', '🇮🇷': 'IR', '🇮🇸': 'IS', '🇮🇹': 'IT', '🇯🇪': 'JE', '🇯🇲': 'JM', '🇯🇴': 'JO', '🇯🇵': 'JP', '🇰🇪': 'KE', '🇰🇬': 'KG', '🇰🇭': 'KH', '🇰🇮': 'KI', '🇰🇲': 'KM', '🇰🇳': 'KN', '🇰🇵': 'KP', '🇰🇷': 'KR', '🇰🇼': 'KW', '🇰🇾': 'KY', '🇰🇿': 'KZ', '🇱🇦': 'LA', '🇱🇧': 'LB', '🇱🇨': 'LC', '🇱🇮': 'LI', '🇱🇰': 'LK', '🇱🇷': 'LR', '🇱🇸': 'LS', '🇱🇹': 'LT', '🇱🇺': 'LU', '🇱🇻': 'LV', '🇱🇾': 'LY', '🇲🇦': 'MA', '🇲🇨': 'MC', '🇲🇩': 'MD', '🇲🇪': 'ME', '🇲🇫': 'MF', '🇲🇬': 'MG', '🇲🇭': 'MH', '🇲🇰': 'MK', '🇲🇱': 'ML', '🇲🇲': 'MM', '🇲🇳': 'MN', '🇲🇴': 'MO', '🇲🇵': 'MP', '🇲🇶': 'MQ', '🇲🇷': 'MR', '🇲🇸': 'MS', '🇲🇹': 'MT', '🇲🇺': 'MU', '🇲🇻': 'MV', '🇲🇼': 'MW', '🇲🇽': 'MX', '🇲🇾': 'MY', '🇲🇿': 'MZ', '🇳🇦': 'NA', '🇳🇨': 'NC', '🇳🇪': 'NE', '🇳🇫': 'NF', '🇳🇬': 'NG', '🇳🇮': 'NI', '🇳🇱': 'NL', '🇳🇴': 'NO', '🇳🇵': 'NP', '🇳🇷': 'NR', '🇳🇺': 'NU', '🇳🇿': 'NZ', '🇴🇲': 'OM', '🇵🇦': 'PA', '🇵🇪': 'PE', '🇵🇫': 'PF', '🇵🇬': 'PG', '🇵🇭': 'PH', '🇵🇰': 'PK', '🇵🇱': 'PL', '🇵🇲': 'PM', '🇵🇳': 'PN', '🇵🇷': 'PR', '🇵🇸': 'PS', '🇵🇹': 'PT', '🇵🇼': 'PW', '🇵🇾': 'PY', '🇶🇦': 'QA', '🇷🇪': 'RE', '🇷🇴': 'RO', '🇷🇸': 'RS', '🇷🇺': 'RU', '🇷🇼': 'RW', '🇸🇦': 'SA', '🇸🇧': 'SB', '🇸🇨': 'SC', '🇸🇩': 'SD', '🇸🇪': 'SE', '🇸🇬': 'SG', '🇸🇭': 'SH', '🇸🇮': 'SI', '🇸🇯': 'SJ', '🇸🇰': 'SK', '🇸🇱': 'SL', '🇸🇲': 'SM', '🇸🇳': 'SN', '🇸🇴': 'SO', '🇸🇷': 'SR', '🇸🇸': 'SS', '🇸🇹': 'ST', '🇸🇻': 'SV', '🇸🇽': 'SX', '🇸🇾': 'SY', '🇸🇿': 'SZ', '🇹🇨': 'TC', '🇹🇩': 'TD', '🇹🇫': 'TF', '🇹🇬': 'TG', '🇹🇭': 'TH', '🇹🇯': 'TJ', '🇹🇰': 'TK', '🇹🇱': 'TL', '🇹🇲': 'TM', '🇹🇳': 'TN', '🇹🇴': 'TO', '🇹🇷': 'TR', '🇹🇹': 'TT', '🇹🇻': 'TV', '🇹🇼': 'TW', '🇹🇿': 'TZ', '🇺🇦': 'UA', '🇺🇬': 'UG', '🇺🇲': 'UM', '🇺🇸': 'US', '🇺🇾': 'UY', '🇺🇿': 'UZ', '🇻🇦': 'VA', '🇻🇨': 'VC', '🇻🇪': 'VE', '🇻🇬': 'VG', '🇻🇮': 'VI', '🇻🇳': 'VN', '🇻🇺': 'VU', '🇼🇫': 'WF', '🇼🇸': 'WS', '🇾🇪': 'YE', '🇾🇹': 'YT', '🇿🇦': 'ZA', '🇿🇲': 'ZM', '🇿🇼': 'ZW'}


@dataclass
class Country:
    alpha_2: str
    alpha_3: str
    name: str
    numeric: int
    emoji: str
    
    @classmethod
    def by_pycountry(cls, country: CountryTyping, emoji: str = "") -> "Country":
        emoji = ""
        alpha_2 = country.alpha_2.upper()
        
        if alpha_2 in emoji_map:
            emoji=emoji_map[alpha_2]
        
        
        return cls(
            alpha_2=country.alpha_2,
            alpha_3=country.alpha_3,
            name=country.name,
            numeric=country.numeric,
            emoji=emoji
        )

    @classmethod
    def by_alpha_2(cls, alpha_2: str) -> "Country":
        return cls.by_pycountry(pycountry.countries.get(alpha_2=alpha_2))
    
    @classmethod
    def by_alpha_3(cls, alpha_3: str) -> "Country":
        return cls.by_pycountry(pycountry.countries.get(alpha_3=alpha_3))
    
    @classmethod
    def by_numeric(cls, numeric: int) -> "Country":
        return cls.by_pycountry(pycountry.countries.get(numeric=numeric))
    
    @classmethod
    def by_name(cls, name: str) -> "Country":
        return cls.by_pycountry(pycountry.countries.get(name=name))
    
    @classmethod
    def by_emoji(cls, flag: str) -> "Country":
        return cls.by_alpha_2(emoji_map[flag])
    
    @classmethod
    def by_official_name(cls, official_name: str) -> "Country":
        return cls.by_pycountry(pycountry.countries.get(official_name=official_name))
    
    def __hash__(self) -> int:
        return hash(self.alpha_3)
    
    def __eq__(self, __value: object) -> bool:
        return self.__hash__() == __value.__hash__()


@dataclass
class Language:
    alpha_2: str
    alpha_3: str
    name: str
    numeric: int

    @classmethod
    def by_pycountry(cls, language) -> Language:
        alpha_2 = language.alpha_2.upper()

        return cls(
            alpha_2=alpha_2,
            alpha_3=language.alpha_3,
            name=language.name,
            numeric=language.numeric,
        )

    @classmethod
    def by_alpha_2(cls, alpha_2: str) -> Language:
        return cls.by_pycountry(pycountry.languages.get(alpha_2=alpha_2))

    @classmethod
    def by_alpha_3(cls, alpha_3: str) -> Language:
        return cls.by_pycountry(pycountry.languages.get(alpha_3=alpha_3))
