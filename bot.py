import json
import urllib.parse
import requests
import os
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from dotenv import load_dotenv
import time
import random
from colorama import init, Fore, Style

init()

load_dotenv()
REFERRAL_CODE = os.getenv("REFERRAL_CODE", "123456789")

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://neura-airdrop-api.onrender.com",
    "referer": f"https://neura-airdrop-api.onrender.com/?tgWebAppStartParam={REFERRAL_CODE}",
    "sec-ch-ua": '"Microsoft Edge";v="136", "Microsoft Edge WebView2";v="136", "Not.A/Brand";v="99", "Chromium";v="136"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
}

headers_referrer = headers.copy()
headers_referrer.update({
    "cache-control": "no-cache",
    "pragma": "no-cache"
})

def print_banner():
    banner = """
╔════════════════════════════════════════════╗
║      🌟 Neura Airdrop Bot                  ║
║ Automate Neura Airdrop tasks and earnings! ║
║ Developed by: https://t.me/sentineldiscus  ║
╚════════════════════════════════════════════╝
    """
    print(banner)

def load_proxies(file_path="proxy.txt"):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            return proxies
        return []
    except Exception:
        return []

def get_proxy(proxies):
    if proxies:
        proxy = random.choice(proxies)
        return {"http": proxy, "https": proxy}
    return None

def decode_user_data(encoded_user):
    try:
        decoded = urllib.parse.unquote(encoded_user)
        user_data = json.loads(decoded)
        return user_data
    except Exception as e:
        print(f"{Fore.RED}Error decoding user data: {str(e)}{Style.RESET_ALL}")
        return None

def extract_auth_date(line):
    try:
        auth_date = line.split("auth_date=")[1].split("&")[0]
        return auth_date
    except Exception as e:
        print(f"{Fore.RED}Error extracting auth_date: {str(e)}{Style.RESET_ALL}")
        return None

def generate_solana_wallet():
    try:
        keypair = Keypair()
        public_key = str(keypair.pubkey())
        private_key = keypair.secret().hex()
        return public_key, private_key
    except Exception as e:
        print(f"{Fore.RED}Error generating Solana wallet: {str(e)}{Style.RESET_ALL}")
        return None, None

def read_data_file(file_path="data.txt"):
    accounts = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                if "user=" in line and "auth_date=" in line:
                    user_part = line.split("user=")[1].split("&")[0]
                    user_data = decode_user_data(user_part)
                    if user_data:
                        auth_date = extract_auth_date(line)
                        if auth_date:
                            user_data["auth_date"] = auth_date
                            accounts.append(user_data)
        if not accounts:
            print(f"{Fore.RED}No valid accounts found in data.txt{Style.RESET_ALL}")
        return accounts
    except Exception as e:
        print(f"{Fore.RED}Error reading data.txt: {str(e)}{Style.RESET_ALL}")
        return []

def load_wallet_data():
    try:
        if os.path.exists("address.json"):
            with open("address.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"{Fore.RED}Error loading address.json: {str(e)}{Style.RESET_ALL}")
        return []

def save_wallet_data(wallet_data):
    try:
        with open("address.json", "w") as f:
            json.dump(wallet_data, f, indent=4)
    except Exception as e:
        print(f"{Fore.RED}Error saving wallet data: {str(e)}{Style.RESET_ALL}")

def has_wallet(user_id, wallet_data):
    for entry in wallet_data:
        if entry["user_id"] == user_id:
            return entry["wallet_address"]
    return None

def register_user(user_data, proxies):
    url = "https://neura-airdrop-api.onrender.com/api/register"
    proxy = get_proxy(proxies)
    payload = {
        "telegramData": {
            "id": user_data["id"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "username": user_data["username"],
            "auth_date": user_data["auth_date"],
            "initial_reward": 999999999999999
        },
        "referralCode": REFERRAL_CODE
    }
    try:
        response = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Register success for user {user_data['username']}{Style.RESET_ALL}")
            return response.json()
        elif response.status_code == 429:
            print(f"{Fore.YELLOW}Rate limit exceeded for user {user_data['username']}. Waiting...{Style.RESET_ALL}")
            time.sleep(60)
            return register_user(user_data, proxies)
        else:
            print(f"{Fore.RED}Register failed for user {user_data['username']}: Status {response.status_code}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error registering user {user_data['username']}: {str(e)}{Style.RESET_ALL}")
        return None

def get_leaderboard(user_id, proxies):
    url = f"https://neura-airdrop-api.onrender.com/api/user-info?userId={user_id}"
    proxy = get_proxy(proxies)
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"{Fore.RED}Leaderboard fetch failed for user {user_id}: Status {response.status_code}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching leaderboard for user {user_id}: {str(e)}{Style.RESET_ALL}")
        return None

def get_referrer_info(proxies):
    url = f"https://neura-airdrop-api.onrender.com/api/referrer-info?code={REFERRAL_CODE}"
    proxy = get_proxy(proxies)
    try:
        response = requests.get(url, headers=headers_referrer, proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Referrer info fetched successfully{Style.RESET_ALL}")
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def complete_task(user_id, username, proxies):
    url = "https://neura-airdrop-api.onrender.com/api/tasks/complete"
    proxy = get_proxy(proxies)
    payload = {
        "userId": user_id,
        "taskId": "twitter_follow",
        "timestamp": int(time.time() * 1000),
        "signature": "61039p"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Task completed for user {username}{Style.RESET_ALL}")
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def set_wallet(user_data, wallet_address, leaderboard_data, proxies):
    url = "https://neura-airdrop-api.onrender.com/api/set-wallet-address"
    proxy = get_proxy(proxies)
    payload = {
        "telegramData": {
            "id": user_data["id"],
            "name": user_data["first_name"],
            "username": user_data["username"],
            "auth_date": user_data["auth_date"],
            "referralCode": leaderboard_data.get("referralCode", REFERRAL_CODE),
            "tokens": leaderboard_data.get("tokens", 0),
            "referrals": leaderboard_data.get("referrals", 0),
            "rank": leaderboard_data.get("rank", 0),
            "wallet_address": "",
            "completedTasks": leaderboard_data.get("completedTasks", {})
        },
        "walletAddress": wallet_address
    }
    try:
        response = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            print(f"{Fore.GREEN}Set wallet success for user {user_data['username']}: Wallet {wallet_address[:8]}...{Style.RESET_ALL}")
            return response.json()
        else:
            print(f"{Fore.RED}Set wallet failed for user {user_data['username']}: Status {response.status_code}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error setting wallet for user {user_data['username']}: {str(e)}{Style.RESET_ALL}")
        return None

def main():
    print_banner()
    proxies = load_proxies()
    accounts = read_data_file()
    if not accounts:
        print(f"{Fore.RED}No accounts found in data.txt{Style.RESET_ALL}")
        return

    wallet_data = load_wallet_data()

    for user_data in accounts:
        print(f"{Fore.CYAN}Processing account: {user_data['username']}{Style.RESET_ALL}")
        
        register_response = register_user(user_data, proxies)
        if not register_response:
            print(f"{Fore.RED}Skipping {user_data['username']} due to register failure{Style.RESET_ALL}")
            continue
        
        leaderboard_response = get_leaderboard(user_data["id"], proxies)
        if not leaderboard_response:
            print(f"{Fore.RED}Skipping {user_data['username']} due to leaderboard failure{Style.RESET_ALL}")
            continue
        
        existing_wallet = has_wallet(user_data["id"], wallet_data)
        if existing_wallet:
            print(f"{Fore.YELLOW}Wallet already set for user {user_data['username']}: {existing_wallet[:8]}...{Style.RESET_ALL}")
        else:
            public_key, private_key = generate_solana_wallet()
            if not public_key:
                print(f"{Fore.RED}Skipping {user_data['username']} due to wallet generation failure{Style.RESET_ALL}")
                continue
            
            set_wallet_response = set_wallet(user_data, public_key, leaderboard_response, proxies)
            if not set_wallet_response:
                print(f"{Fore.RED}Skipping wallet save for {user_data['username']} due to set wallet failure{Style.RESET_ALL}")
                continue
            
            wallet_data.append({
                "username": user_data["username"],
                "user_id": user_data["id"],
                "wallet_address": public_key,
                "private_key": private_key
            })
            save_wallet_data(wallet_data)
            print(f"{Fore.GREEN}Set wallet success for user {user_data['username']}: Wallet {public_key[:8]}...{Style.RESET_ALL}")
        
        get_referrer_info(proxies)
        complete_task(user_data["id"], user_data["username"], proxies)
        print(f"{Fore.GREEN}Leaderboard fetched for user {user_data['id']}: Tokens {leaderboard_response.get('tokens', 0)}, Rank {leaderboard_response.get('rank', 0)}{Style.RESET_ALL}")
        time.sleep(5)

if __name__ == "__main__":
    main()
