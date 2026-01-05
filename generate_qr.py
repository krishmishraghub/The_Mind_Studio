#!/usr/bin/env python3
"""
QR Code Generator for Mental Well-being Agent Frontend
Generates a QR code that users can scan to access the questionnaire.
"""

import sys
import os

# Try to import qrcode, with helpful error message if missing
try:
    import qrcode
except ImportError:
    print("❌ Error: qrcode module not found!")
    print("\n💡 Solution: Activate virtual environment first:")
    print("   source .venv/bin/activate")
    print("   python generate_qr.py <URL>")
    print("\nOr install it:")
    print("   pip install qrcode[pil]")
    sys.exit(1)
import sys
import os
from urllib.parse import urlparse

def generate_qr_code(url: str, output_path: str = "qr_code.png"):
    """
    Generate a QR code for the given URL.
    
    Args:
        url: The URL to encode in the QR code
        output_path: Path where the QR code image will be saved
    """
    # Validate URL
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format")
    except Exception as e:
        print(f"Error: Invalid URL - {e}")
        print("Please provide a valid URL (e.g., http://localhost:8000 or https://yourdomain.com)")
        return False
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    img.save(output_path)
    print(f"✅ QR code generated successfully!")
    print(f"📱 File saved as: {output_path}")
    print(f"🔗 URL encoded: {url}")
    print(f"\n💡 Tip: Print this QR code or display it on a screen for participants to scan.")
    return True


def get_local_ip():
    """Get the local IP address of the machine."""
    import socket
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def main():
    """Main function to generate QR code."""
    print("=" * 60)
    print("  Mental Well-being Agent - QR Code Generator")
    print("=" * 60)
    print()
    
    # Get URL from command line or prompt user
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Enter the URL for your deployed frontend:")
        print("  Examples:")
        print("    - Local: http://localhost:8000")
        print("    - Local network: http://192.168.1.100:8000")
        print("    - Deployed: https://yourdomain.com")
        print()
        
        # Try to auto-detect local IP
        local_ip = get_local_ip()
        default_url = f"http://{local_ip}:8000"
        
        url = input(f"URL [{default_url}]: ").strip()
        if not url:
            url = default_url
    
    # Ensure URL doesn't end with /
    url = url.rstrip('/')
    
    # Generate QR code
    output_file = "qr_code.png"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    success = generate_qr_code(url, output_file)
    
    if success:
        print()
        print("=" * 60)
        print("  Next Steps:")
        print("=" * 60)
        print("1. Make sure your backend server is running:")
        print("   python app.py")
        print()
        print("2. Display the QR code (qr_code.png) on a screen or print it")
        print()
        print("3. Participants can scan the QR code with their phone camera")
        print("   to access the mental well-being questionnaire")
        print("=" * 60)


if __name__ == "__main__":
    main()

