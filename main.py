import os
import requests
import random
import string
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
import threading
import sys
import json

console = Console(highlight=False)
# dont worry got fix to prevent underscore at end or start
def generate_username(length, use_numbers, use_underscores):
    characters = string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_underscores:
        characters += "_"

    while True:
        username = ''.join(random.choice(characters) for _ in range(length))
        if use_underscores and username.count("_") > 1:
            continue
        if use_underscores and (username.startswith("_") or username.endswith("_")):
            continue
        yield username

def check_username(username):
    url = f"https://auth.roblox.com/v2/usernames/validate?request.username={username}&request.birthday=04%2F15%2F02&request.context=Signup" # yeah it is that simple
    try:
        response = requests.get(url)
        data = response.json()
        if 'message' in data:
            return data["message"] == "Username is valid"
        else:
            cprint("red", f"Error: Invalid API response for {username}")
            return False
    except json.decoder.JSONDecodeError:
        cprint("red", f"Error: Invalid JSON response for {username}")
        return False
    except Exception as e:
        cprint("red", f"Error: Unable to connect to API for {username}")
        return False



def cprint(color: str, content: str) -> None:
    console.print(f"[bold {color}]{content}[/bold {color}]")

def main():
    #custom_file_check = input("Do you want to check a custom filename for valid usernames? (y/n): ")
    
    if False:#custom_file_check.lower() == "y":
        custom_filename = input("Enter a custom filename for valid usernames (without extension): ")
        valid_username_file = f"valids/{custom_filename}_valid.txt"

        if not os.path.exists(valid_username_file):
            with open(valid_username_file, "w") as file:
                pass

    else:
        length = int(input("Enter the desired username length: "))
        valid_username_file = f"valids/{length}_valid.txt"

        if not os.path.exists(valid_username_file):
            with open(valid_username_file, "w") as file:
                pass

    use_numbers = input("Do you want to use numbers in the username? (y/n): ").lower() == "y"
    use_underscores = input("Do you want to use underscores in the username? (y/n): ").lower() == "y"

    num_valid_usernames = int(input("Enter the number of valid usernames to generate: "))
    username_generator = generate_username(length, use_numbers, use_underscores)

    existing_usernames = set()  # Use a set to track existing usernames
    max_iterations = 1000  # Number of iterations before clearing the set
    current_iterations = 0
    valid_count = 0
    
    num_threads = int(input("Enter the number of threads to use: "))
    
    def input_thread():
        #nonlocal custom_file_check
        while True:
            key = input()
            if key.lower() == 'q':
                print("Program canceled by user.")
                os._exit(0)
            else:
                main()  # Restart the program
            
    input_thread = threading.Thread(target=input_thread)
    input_thread.daemon = True
    input_thread.start()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        while valid_count < num_valid_usernames:
            try:
                new_username = next(username_generator)
                is_valid = check_username(new_username)
                if executor.submit(check_and_print, new_username, valid_username_file, existing_usernames, is_valid, valid_count, num_valid_usernames):
                    if is_valid:
                        valid_count += 1  # Only increment for valid usernames

                current_iterations += 1

                if current_iterations >= max_iterations:
                    existing_usernames.clear()
                    current_iterations = 0
            except KeyboardInterrupt:
                print("Program canceled by user.")
                os._exit(0)
    
    print("Generating finished! Press enter to go again.")
    key = input()
    if key.lower() == 'q':
        print("Exiting the program.")
        os._exit(0)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
        main()

def check_and_print(new_username, valid_username_file, existing_usernames, is_valid, valid_count, num_valid_usernames):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    
    if is_valid:
        with open(valid_username_file, "a") as file:
            #if custom_file_check.lower() != "y" and new_username in existing_usernames:
            #    return False
            
            progress = f"[{valid_count + 1}/{num_valid_usernames}]"
            
            if new_username in existing_usernames:
                cprint("orange", f"{timestamp} Username found but is a duplicate! - {new_username}")
            else:
                existing_usernames.add(new_username)
                file.write(new_username + "\n")
                cprint("green", f"{timestamp} {progress} Username found! - {new_username}")
                return True
    else:
        cprint("red", f"{timestamp} Username taken! - {new_username}")
    
    return False

if __name__ == "__main__":
    main()
