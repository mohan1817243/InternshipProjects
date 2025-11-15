import hashlib
import itertools
import string
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import argparse

# Supported hash types
HASH_TYPES = [
    "md5", "sha1", "sha224", "sha256", "sha384", 
    "sha512", "sha3_224", "sha3_256", "sha3_512"
]

def password_generator(min_length, max_length, characters):
    """Generate passwords of specified lengths"""
    for length in range(min_length, max_length + 1):
        for password in itertools.product(characters, repeat=length):
            yield "".join(password)

def check_hash(hash_fn, password, target_hash):
    """Check if password matches the target hash"""
    try:
        return hash_fn(password.encode()).hexdigest() == target_hash
    except:
        return False

def crack_hash(target_hash, wordlist=None, hash_type='md5', min_length=1, max_length=4, 
               characters=None, max_workers=8):
    """Main hash cracking function"""
    
    # Set default characters
    if characters is None:
        characters = string.ascii_letters + string.digits
    
    # Validate hash type
    if hash_type not in HASH_TYPES:
        print(f"❌ Error: Unsupported hash type '{hash_type}'")
        print(f"✅ Supported: {', '.join(HASH_TYPES)}")
        return None
    
    hash_fn = getattr(hashlib, hash_type)
    
    print(f"🔍 Cracking {hash_type.upper()} hash: {target_hash}")
    print("=" * 50)
    
    # Wordlist attack
    if wordlist:
        try:
            with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            print(f"📁 Using wordlist: {len(passwords):,} passwords")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(check_hash, hash_fn, pwd, target_hash): pwd 
                    for pwd in passwords
                }
                
                # Check results with progress bar
                for future in tqdm(futures, total=len(passwords), desc="Checking passwords"):
                    if future.result():
                        return futures[future]
                        
        except FileNotFoundError:
            print(f"❌ Wordlist file '{wordlist}' not found")
            return None
    
    # Brute force attack
    else:
        # Safety check for brute force
        if max_length > 6:
            print("⚠️  Warning: Brute force limited to 6 characters for performance")
            max_length = 6
        
        total_combinations = sum(len(characters) ** length for length in range(min_length, max_length + 1))
        print(f"🔧 Brute force: lengths {min_length}-{max_length}")
        print(f"📊 Total combinations: {total_combinations:,}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            # Submit password checking tasks
            for password in password_generator(min_length, max_length, characters):
                future = executor.submit(check_hash, hash_fn, password, target_hash)
                futures[future] = password
            
            # Check results with progress bar
            for future in tqdm(futures, total=total_combinations, desc="Brute forcing"):
                if future.result():
                    return futures[future]
    
    return None

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="🔓 Password Hash Cracker")
    parser.add_argument('hash', help="The hash to crack")
    parser.add_argument('-w', '--wordlist', help="Path to password wordlist file")
    parser.add_argument('--hash-type', choices=HASH_TYPES, default='md5', 
                       help="Hash type (default: md5)")
    parser.add_argument('--min-length', type=int, default=1, 
                       help="Min password length for brute force (default: 1)")
    parser.add_argument('--max-length', type=int, default=4, 
                       help="Max password length for brute force (default: 4)")
    parser.add_argument('-c', '--characters', default=string.ascii_letters + string.digits,
                       help="Characters for brute force (default: letters + digits)")
    parser.add_argument('--max-workers', type=int, default=8,
                       help="Number of threads (default: 8)")
    
    args = parser.parse_args()
    
    # Crack the hash
    cracked_password = crack_hash(
        target_hash=args.hash,
        wordlist=args.wordlist,
        hash_type=args.hash_type,
        min_length=args.min_length,
        max_length=args.max_length,
        characters=args.characters,
        max_workers=args.max_workers
    )
    
    # Show result
    print("\n" + "=" * 50)
    if cracked_password:
        print(f"🎉 PASSWORD FOUND: {cracked_password}")
    else:
        print("❌ Password not found")

if __name__ == "__main__":
    main()