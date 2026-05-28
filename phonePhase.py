import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import sys
import requests
import webbrowser
from bs4 import BeautifulSoup
import urllib.parse
import time

class PhonePhase:
    def __init__(self, phone_number):
        self.raw_number = phone_number
        self.parsed_number = None
        self.info = {}
        self.error = None

    def parse(self):
        try:
            self.parsed_number = phonenumbers.parse(self.raw_number)
            if not phonenumbers.is_possible_number(self.parsed_number):
                self.error = "The number is not possible."
                return False
            return True
        except Exception as e:
            self.error = str(e)
            return False

    def get_basic_info(self):
        is_valid = phonenumbers.is_valid_number(self.parsed_number)
        
        self.info["Basic Information"] = {
            "Original Number": self.raw_number,
            "Valid Number": "Yes" if is_valid else "No",
            "International Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "National Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
            "E164 Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164),
            "Country Code": self.parsed_number.country_code,
            "National Number": self.parsed_number.national_number,
        }

        # Number Type
        number_type = phonenumbers.number_type(self.parsed_number)
        type_mapping = {
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VOIP",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "UAN",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        }
        self.info["Basic Information"]["Number Type"] = type_mapping.get(number_type, "Unknown")

    def get_provider_info(self):
        self.info["Provider & Location"] = {
            "Location": geocoder.description_for_number(self.parsed_number, "en") or "Unknown",
            "Carrier": carrier.name_for_number(self.parsed_number, "en") or "Unknown",
            "Timezones": ", ".join(timezone.time_zones_for_number(self.parsed_number)) or "Unknown",
        }

    def get_social_media_links(self):
        e164 = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164).replace("+", "")
        self.info["Social Media & Messaging (Direct Links)"] = {
            "WhatsApp": f"https://wa.me/{e164}",
            "Telegram": f"https://t.me/+{e164}",
            "Viber": f"viber://add?number={e164}",
            "Skype": f"skype:{e164}?chat"
        }

    def get_reputation_hints(self):
        e164 = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164)
        self.info["External Reputation Lookups"] = {
            "Truecaller": f"https://www.truecaller.com/search/global/{urllib.parse.quote(e164)}",
            "Sync.me": f"https://sync.me/search/?number={urllib.parse.quote(e164)}",
            "Whoscall": f"https://whoscall.com/en/search/{urllib.parse.quote(e164)}",
            "FreeSpoke": f"https://freespoke.com/search?q={urllib.parse.quote(e164)}"
        }

    def generate_osint_queries(self):
        e164 = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164)
        national = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        # Various formats for searching
        search_formats = [e164, national, self.raw_number]
        queries = []
        for fmt in set(search_formats):
            queries.append(f'"{fmt}"')
        
        dorks = [
            f'site:facebook.com "{e164}"',
            f'site:twitter.com "{e164}"',
            f'site:instagram.com "{e164}"',
            f'site:linkedin.com "{e164}"',
            f'site:github.com "{e164}"',
            f'site:pastebin.com "{e164}"',
            f'site:truecaller.com "{e164}"',
            f'site:craigslist.org "{e164}"',
            f'site:ebay.com "{e164}"',
            f'"{e164}" leaked',
            f'"{e164}" owner'
        ]
        
        self.info["OSINT Search Queries (Deep Recon)"] = queries + dorks

    def get_breach_and_leak_links(self):
        e164 = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164)
        self.info["Data Breach & Leak Lookups"] = {
            "DeHashed (Paid)": f"https://www.dehashed.com/search?query={urllib.parse.quote(e164)}",
            "IntelligenceX": f"https://intelx.io/?s={urllib.parse.quote(e164)}",
            "HaveIBeenPwned": f"https://haveibeenpwned.com/search?q={urllib.parse.quote(e164)}",
            "Snusbase": f"https://snusbase.com/search/{urllib.parse.quote(e164)}"
        }

    def scam_analysis_and_risk(self):
        number_type = phonenumbers.number_type(self.parsed_number)
        risk_score = 0
        factors = []

        if number_type == phonenumbers.PhoneNumberType.VOIP:
            risk_score += 40
            factors.append("VOIP Number (High anonymity)")
        if number_type == phonenumbers.PhoneNumberType.PREMIUM_RATE:
            risk_score += 60
            factors.append("Premium Rate Number (Potential Fraud)")
        if not phonenumbers.is_valid_number(self.parsed_number):
            risk_score += 20
            factors.append("Invalid Format")
        
        # Add basic logic for carrier-based risk if known
        carrier_name = carrier.name_for_number(self.parsed_number, "en").lower()
        if "google voice" in carrier_name or "textnow" in carrier_name:
            risk_score += 30
            factors.append(f"Virtual Carrier detected: {carrier_name}")

        self.info["AI Scammer Profiling & Risk"] = {
            "Risk Score": f"{min(risk_score, 100)}/100",
            "Risk Factors": ", ".join(factors) if factors else "None detected",
            "Trust Level": "Low" if risk_score > 50 else "Medium" if risk_score > 20 else "High"
        }

    def run_all(self):
        if self.parse():
            self.get_basic_info()
            self.get_provider_info()
            self.get_social_media_links()
            self.get_reputation_hints()
            self.generate_osint_queries()
            self.get_breach_and_leak_links()
            self.scam_analysis_and_risk()
            return True
        return False

def print_banner():
    banner = """
    ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██████╗ ██╗  ██╗ █████╗ ███████╗███████╗
    ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔══██╗██║  ██║██╔══██╗██╔════╝██╔════╝
    ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  ██████╔╝███████║███████║███████╗█████╗  
    ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██╔═══╝ ██╔══██║██╔══██║╚════██║██╔══╝  
    ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗██║     ██║  ██║██║  ██║███████║███████╗
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
                                  made by TwilightRaaz

         		   Github -- github.com/TwilightRaaz 
    """
    print(banner)

def main():
    print_banner()
    
    if len(sys.argv) > 1:
        number = sys.argv[1]
    else:
        number = input("\n[?] Enter phone number (with country code, e.g., +14155552671): ").strip()

    if not number:
        print("[!] Error: No number provided.")
        return

    print(f"\n[*] Analyzing {number}...")
    time.sleep(2)

    scanner = PhonePhase(number)
    if scanner.run_all():
        for section, data in scanner.info.items():
            print(f"\n--- {section} ---")
            if isinstance(data, list):
                for item in data:
                    print(f"  > {item}")
            else:
                for key, value in data.items():
                    print(f"  {key:<25}: {value}")
        
        print("\n[+] Analysis Complete.")
        print("[!] Tip: Use the 'External Reputation Lookups' links for crowd-sourced name identification.")
    else:
        print(f"\n[!] Error: {scanner.error}")

if __name__ == "__main__":
    main()
