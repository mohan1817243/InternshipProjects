import pikepdf
import argparse
import string
from tqdm import tqdm

def try_password(pdf_file, password):
    """Try to open PDF with given password"""
    try:
        with pikepdf.open(pdf_file, password=password) as pdf:
            return password
    except pikepdf.PasswordError:
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def load_wordlist(wordlist_file):
    """Load passwords from wordlist file"""
    try:
        with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as file:
            passwords = [line.strip() for line in file if line.strip()]
        return passwords
    except FileNotFoundError:
        print(f"❌ Wordlist file '{wordlist_file}' not found")
        return []

def generate_passwords(min_len=1, max_len=3, charset=None):
    """Generate passwords of specified length"""
    if charset is None:
        charset = string.ascii_lowercase + string.digits
    
    passwords = []
    # Simple password generation for short lengths
    if max_len <= 4:
        from itertools import product
        for length in range(min_len, max_len + 1):
            for pwd_tuple in product(charset, repeat=length):
                passwords.append(''.join(pwd_tuple))
    
    return passwords

def main():
    parser = argparse.ArgumentParser(description='PDF Password Cracker')
    parser.add_argument('pdf_file', help='Path to the encrypted PDF file')
    parser.add_argument('--wordlist', help='Path to password wordlist file')
    parser.add_argument('--generate', action='store_true', 
                       help='Generate simple passwords (max 4 chars)')
    parser.add_argument('--min', type=int, default=1, 
                       help='Min password length for generation')
    parser.add_argument('--max', type=int, default=3, 
                       help='Max password length for generation')
    
    args = parser.parse_args()
    
    print("🔓 PDF Password Cracker")
    print("=" * 30)
    
    # Get passwords to try
    if args.wordlist:
        passwords = load_wordlist(args.wordlist)
        if not passwords:
            return
        print(f"📁 Loaded {len(passwords)} passwords from wordlist")
        
    elif args.generate:
        if args.max > 4:
            print("⚠️  Warning: Generation limited to 4 characters for performance")
            args.max = 4
        
        passwords = generate_passwords(args.min, args.max)
        print(f"🔧 Generated {len(passwords)} passwords")
        
    else:
        print("❌ Please provide either --wordlist or --generate")
        return
    
    print(f"🎯 Target: {args.pdf_file}")
    print(f"🔑 Trying {len(passwords)} passwords...")
    print("-" * 30)
    
    # Try passwords
    found = False
    for password in tqdm(passwords, desc="Cracking", unit="pwd"):
        result = try_password(args.pdf_file, password)
        if result:
            print(f"\n🎉 SUCCESS! Password found: {password}")
            found = True
            break
    
    if not found:
        print("\n❌ Password not found in the list")

if __name__ == "__main__":
    main()