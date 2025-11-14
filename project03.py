import PyPDF2
import sys
import os

def create_password_protected_pdf(input_pdf, output_pdf, password):
    # Check if input file exists
    if not os.path.exists(input_pdf):
        print(f"❌ Error: Input file '{input_pdf}' not found")
        return False
    
    # Check if input is a PDF
    if not input_pdf.lower().endswith('.pdf'):
        print("❌ Error: Input file must be a PDF")
        return False
    
    try:
        # Read input PDF
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Encrypt with password
            pdf_writer.encrypt(password)
            
            # Write output PDF
            with open(output_pdf, 'wb') as output:
                pdf_writer.write(output)
        
        print(f"✅ Success! Password-protected PDF saved as: {output_pdf}")
        return True
        
    except PyPDF2.PdfReadError:
        print("❌ Error: Cannot read PDF file - file may be corrupted")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    return False

def main():
    # Simple command line handling
    if len(sys.argv) != 4:
        print("🔒 PDF Encryption Tool")
        print("Usage: python pdf_encrypt.py <input.pdf> <output.pdf> <password>")
        print("\nExample:")
        print("python pdf_encrypt.py document.pdf secure_document.pdf mypassword")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    password = sys.argv[3]
    
    # Basic validation
    if not password:
        print("❌ Error: Password cannot be empty")
        sys.exit(1)
    
    # Create protected PDF
    success = create_password_protected_pdf(input_pdf, output_pdf, password)
    
    if success:
        print("🎉 Encryption completed successfully!")
    else:
        print("💥 Encryption failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()