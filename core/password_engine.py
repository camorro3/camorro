#!/usr/bin/env python3
"""
Camoro AI Password Generation Engine
Generates intelligent password combinations based on target intelligence.
Uses pattern-based mutations and AI-enhanced combinatorial generation.
"""

import itertools
import random
import string
from datetime import datetime
from .config import (
    MUTATION_PATTERNS, LEET_MAP, TARGET_PASSWORD_COUNT, MAX_COMBINATIONS
)

class PasswordEngine:
    """AI-Powered Password Generation Engine."""
    
    def __init__(self, target_data, personal_info):
        """
        Initialize with target data and user-provided personal information.
        
        Args:
            target_data: Dict from info_gather module
            personal_info: Dict with user-provided personal details
                {
                    "real_name": "",
                    "birth_date": "",  # DD/MM/YYYY or YYYY-MM-DD
                    "birth_day": "",
                    "birth_month": "",
                    "birth_year": "",
                    "girlfriend_name": "",
                    "pet_name": "",
                    "favorite_thing": "",
                    "nickname": "",
                    "phone_number": "",
                    "additional_words": [],
                }
        """
        self.target_data = target_data
        self.personal = personal_info
        self.word_pool = []
        self.generated_passwords = set()
        
        self._build_word_pool()
    
    def _build_word_pool(self):
        """Build comprehensive word pool from all sources."""
        pool = set()
        
        # From target profile
        pool.update(self.target_data.get("extracted_names", []))
        pool.update(self.target_data.get("extracted_keywords", []))
        
        # Username variants
        username = self.target_data.get("username", "").lower()
        pool.add(username)
        pool.add(username.replace("_", "").replace(".", ""))
        
        # From personal info
        if self.personal.get("real_name"):
            name_parts = self.personal["real_name"].lower().split()
            pool.update(name_parts)
            pool.add(self.personal["real_name"].lower().replace(" ", ""))
            # First name
            if name_parts:
                pool.add(name_parts[0])
                # Capitalized
                pool.add(name_parts[0].capitalize())
        
        if self.personal.get("girlfriend_name"):
            gf = self.personal["girlfriend_name"].lower()
            pool.add(gf)
            pool.add(gf.capitalize())
            gf_parts = gf.split()
            pool.update(gf_parts)
        
        if self.personal.get("pet_name"):
            pet = self.personal["pet_name"].lower()
            pool.add(pet)
            pool.add(pet.capitalize())
        
        if self.personal.get("nickname"):
            nick = self.personal["nickname"].lower()
            pool.add(nick)
            pool.add(nick.capitalize())
        
        if self.personal.get("favorite_thing"):
            fav = self.personal["favorite_thing"].lower()
            pool.add(fav)
        
        if self.personal.get("phone_number"):
            phone = self.personal["phone_number"]
            pool.add(phone)
            if len(phone) >= 4:
                pool.add(phone[-4:])   # Last 4 digits
                pool.add(phone[-6:])   # Last 6 digits
        
        # Additional custom words
        pool.update([w.lower() for w in self.personal.get("additional_words", [])])
        
        # Remove empty and single char
        self.word_pool = [w for w in pool if len(w) > 1]
        
        # Sort by relevance (longer words first = more likely meaningful)
        self.word_pool.sort(key=len, reverse=True)
    
    def _get_date_components(self):
        """Extract all date components from birth date."""
        components = {
            "day": "",
            "month": "",
            "year": "",
            "short_year": "",
            "month_num": "",
            "day_month": "",
            "month_day": "",
            "day_month_year": "",
            "month_day_year": "",
            "full_date": "",
            "reverse_date": "",
        }
        
        birth = self.personal.get("birth_date", "")
        day = self.personal.get("birth_day", "")
        month = self.personal.get("birth_month", "")
        year = self.personal.get("birth_year", "")
        
        # Parse from combined string
        if birth:
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.strptime(birth, fmt)
                    day = str(dt.day).zfill(2)
                    month = str(dt.month).zfill(2)
                    year = str(dt.year)
                    break
                except ValueError:
                    continue
        
        if day:
            components["day"] = day.zfill(2)
        if month:
            components["month"] = month.zfill(2)
            # Month name
            try:
                month_names = ["january", "february", "march", "april", "may", "june",
                             "july", "august", "september", "october", "november", "december"]
                idx = int(month) - 1
                if 0 <= idx < 12:
                    components["month_name"] = month_names[idx]
            except ValueError:
                pass
        
        if year:
            components["year"] = year
            components["short_year"] = year[-2:]
        
        if day and month and year:
            components["day_month"] = f"{day}{month}"
            components["month_day"] = f"{month}{day}"
            components["day_month_year"] = f"{day}{month}{year}"
            components["month_day_year"] = f"{month}{day}{year}"
            components["full_date"] = f"{day}{month}{year}"
            components["reverse_date"] = f"{year}{month}{day}"
            components["short_date"] = f"{day}{month}{year[-2:]}"
        elif day and month:
            components["day_month"] = f"{day}{month}"
            components["month_day"] = f"{month}{day}"
        
        return components
    
    def _apply_mutations(self, word, mutation_pattern, date_comps, num_range):
        """Apply a single mutation pattern to a word."""
        result = mutation_pattern
        
        # Replace placeholders
        result = result.replace("{word}", word)
        result = result.replace("{capitalize}", word.capitalize())
        result = result.replace("{upper}", word.upper())
        result = result.replace("{leet}", word.translate(LEET_MAP))
        result = result.replace("{reverse}", word[::-1])
        
        # Date components
        for key, val in date_comps.items():
            if val:
                result = result.replace(f"{{{key}}}", val)
        
        # Numbers
        if "{num}" in result:
            for _ in range(3):  # Try 3 random numbers
                num = str(random.randint(0, num_range))
                yield result.replace("{num}", num, 1)
        elif "{num1}" in result and "{num2}" in result:
            n1 = str(random.randint(0, 99))
            n2 = str(random.randint(0, 99))
            yield result.replace("{num1}", n1).replace("{num2}", n2)
        else:
            yield result
        
        # Special chars
        if "{special}" in result:
            for sp in ["!", "@", "#", "$", "%", "&", "*"]:
                yield result.replace("{special}", sp)
    
    def generate_passwords(self, target_count=TARGET_PASSWORD_COUNT):
        """
        Generate password combinations.
        Target: ~18,000 intelligent passwords.
        """
        print(f"\n{C}[*] AI Password Engine Initializing...{RE}")
        print(f"{Y}[*] Word pool size: {len(self.word_pool)} unique words{RE}")
        
        date_comps = self._get_date_components()
        num_range = 9999
        
        # Phase 1: Basic word + number combinations
        basic_passwords = set()
        for word in self.word_pool[:30]:
            word_variants = [word, word.capitalize(), word.upper(), 
                           word.lower(), word.translate(LEET_MAP)]
            
            for variant in word_variants:
                if len(variant) >= 3:
                    # Word + numbers
                    for num in range(0, 100):
                        basic_passwords.add(f"{variant}{num}")
                        basic_passwords.add(f"{variant}{num:02d}")
                    # Word + year
                    for year in range(1970, 2026):
                        if len(basic_passwords) > target_count * 0.3:
                            break
                        basic_passwords.add(f"{variant}{year}")
                    # Numbers first
                    for num in range(0, 100):
                        basic_passwords.add(f"{num}{variant}")
        
        print(f"{G}[+] Phase 1 (Basic): {len(basic_passwords):,} passwords{RE}")
        
        # Phase 2: Date-based combinations
        date_passwords = set()
        valid_date_parts = {k: v for k, v in date_comps.items() if v}
        
        for word in self.word_pool[:20]:
            for date_key, date_val in valid_date_parts.items():
                if len(date_val) >= 2:
                    date_passwords.add(f"{word}{date_val}")
                    date_passwords.add(f"{date_val}{word}")
                    date_passwords.add(f"{word}_{date_val}")
                    date_passwords.add(f"{word}{date_val}!")
                    date_passwords.add(f"{word.capitalize()}{date_val}")
                    
                    # Include year variants
                    if len(date_val) == 4 and date_val.isdigit():
                        short = date_val[-2:]
                        date_passwords.add(f"{word}{short}")
                        date_passwords.add(f"{short}{word}")
        
        print(f"{G}[+] Phase 2 (Date-based): {len(date_passwords):,} passwords{RE}")
        
        # Phase 3: Two-word combinations
        combo_passwords = set()
        top_words = self.word_pool[:15]
        
        for w1, w2 in itertools.combinations(top_words, 2):
            if len(combo_passwords) > target_count * 0.2:
                break
            for n in [0, 1, 12, 123, 1234, 2023, 2024, 2025, 2026]:
                combo_passwords.add(f"{w1}{w2}")
                combo_passwords.add(f"{w1}_{w2}")
                combo_passwords.add(f"{w1}{w2}{n}")
                combo_passwords.add(f"{w1.capitalize()}{w2}")
                combo_passwords.add(f"{w1}{w2.capitalize()}")
        
        print(f"{G}[+] Phase 3 (Combinations): {len(combo_passwords):,} passwords{RE}")
        
        # Phase 4: Leet speak and special chars
        leet_passwords = set()
        for word in self.word_pool[:25]:
            leet_word = word.translate(LEET_MAP)
            if leet_word != word:
                for suffix in ["", "!", "@", "#", "123", "007"]:
                    leet_passwords.add(f"{leet_word}{suffix}")
                    leet_passwords.add(f"{leet_word.capitalize()}{suffix}")
        
        print(f"{G}[+] Phase 4 (Leet): {len(leet_passwords):,} passwords{RE}")
        
        # Phase 5: Pattern-based mutations
        pattern_passwords = set()
        for word in self.word_pool[:10]:
            for pattern_type, patterns in MUTATION_PATTERNS.items():
                for pattern in patterns:
                    for result in self._apply_mutations(word, pattern, date_comps, num_range):
                        if len(result) >= 6:  # Instagram min password length
                            pattern_passwords.add(result)
        
        print(f"{G}[+] Phase 5 (Patterns): {len(pattern_passwords):,} passwords{RE}")
        
        # Phase 6: Common password patterns
        common_suffixes = ["123", "1234", "12345", "123456", "!", "@", "#", "2024", "2025", 
                          "2026", "007", "007!", "1", "2", "3", "11", "22", "33"]
        common_passwords = set()
        
        for word in self.word_pool[:20]:
            for suffix in common_suffixes:
                common_passwords.add(f"{word}{suffix}")
                common_passwords.add(f"{word.capitalize()}{suffix}")
                common_passwords.add(f"{word.upper()}{suffix}")
        
        print(f"{G}[+] Phase 6 (Common patterns): {len(common_passwords):,} passwords{RE}")
        
        # Phase 7: AI-Enhanced - contextual mutations based on profile analysis
        ai_passwords = self._ai_contextual_generation()
        print(f"{G}[+] Phase 7 (AI Contextual): {len(ai_passwords):,} passwords{RE}")
        
        # Combine all phases
        all_passwords = set()
        all_passwords.update(basic_passwords)
        all_passwords.update(date_passwords)
        all_passwords.update(combo_passwords)
        all_passwords.update(leet_passwords)
        all_passwords.update(pattern_passwords)
        all_passwords.update(common_passwords)
        all_passwords.update(ai_passwords)
        
        # Filter and sort
        all_passwords = {
            p for p in all_passwords 
            if 6 <= len(p) <= 40  # Instagram password length constraints
            and not p.startswith(" ") 
            and not p.endswith(" ")
        }
        
        # Trim to target count
        final_list = list(all_passwords)
        random.shuffle(final_list)
        final_list = final_list[:target_count]
        
        print(f"\n{G}[✓] Generated {len(final_list):,} intelligent passwords{RE}")
        return final_list
    
    def _ai_contextual_generation(self):
        """
        AI-Enhanced contextual password generation.
        Analyzes profile patterns and generates intelligent guesses.
        """
        passwords = set()
        
        # Analyze username patterns
        username = self.target_data.get("username", "").lower()
        full_name = self.target_data.get("full_name", "").lower()
        bio = self.target_data.get("biography", "").lower()
        
        # Common username + year patterns
        for year in range(1980, 2026):
            passwords.add(f"{username}{year}")
            passwords.add(f"{username}_{year}")
            passwords.add(f"{year}{username}")
        
        # Birthday year patterns
        birth_year = self.personal.get("birth_year", "")
        if birth_year:
            passwords.add(f"{username}{birth_year}")
            passwords.add(f"{username}_{birth_year}")
            passwords.add(f"{username}{birth_year[-2:]}")
        
        # Name-based intelligent patterns
        real_name = self.personal.get("real_name", "").lower()
        if real_name and " " in real_name:
            first, *rest = real_name.split()
            if rest:
                last = rest[-1]
                passwords.add(f"{first}{last}")
                passwords.add(f"{first[0]}{last}")
                passwords.add(f"{first}.{last}")
                passwords.add(f"{first}_{last}")
                passwords.add(f"{first}{last}{birth_year}" if birth_year else f"{first}{last}")
        
        # Girlfriend/boyfriend patterns
        gf = self.personal.get("girlfriend_name", "").lower()
        if gf and real_name:
            first_name = real_name.split()[0] if " " in real_name else real_name
            passwords.add(f"{first_name}+{gf}")
            passwords.add(f"{first_name}love{gf}")
            passwords.add(f"{gf}love{first_name}")
            passwords.add(f"{first_name}&{gf}")
            passwords.add(f"{first_name}and{gf}")
            passwords.add(f"{gf}and{first_name}")
        
        # Pet-based patterns
        pet = self.personal.get("pet_name", "").lower()
        if pet:
            for num in ["", "1", "123", "007", "2024"]:
                passwords.add(f"{pet}{num}")
                passwords.add(f"{pet.capitalize()}{num}")
                passwords.add(f"my{pet}{num}")
                passwords.add(f"ilove{pet}{num}")
        
        # Phone number patterns
        phone = self.personal.get("phone_number", "")
        if phone and len(phone) >= 4:
            for word in [username, real_name.split()[0] if real_name else username, pet, gf]:
                if word:
                    passwords.add(f"{word}{phone[-4:]}")
                    passwords.add(f"{word}{phone[-6:]}")
                    passwords.add(f"{word}@{phone[-4:]}")
        
        # Bio keyword combinations
        keywords = self.target_data.get("extracted_keywords", [])
        for kw1, kw2 in itertools.combinations(keywords[:5], 2):
            if len(kw1) > 2 and len(kw2) > 2:
                passwords.add(f"{kw1}{kw2}")
                passwords.add(f"{kw1}_{kw2}")
        
        # Nickname patterns
        nickname = self.personal.get("nickname", "").lower()
        if nickname:
            for year in range(2000, 2026):
                passwords.add(f"{nickname}{year}")
            passwords.add(f"{nickname}007")
            passwords.add(f"{nickname}123")
        
        # Favorite thing + numbers
        fav = self.personal.get("favorite_thing", "").lower()
        if fav:
            for num in ["123", "007", "2024", "2025", "1", "99", "00"]:
                passwords.add(f"{fav}{num}")
                passwords.add(f"{fav.capitalize()}{num}")
        
        return passwords
