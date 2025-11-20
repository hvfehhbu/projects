import win32com.client
import sys

try:
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    print("Word is available.")
    word.Quit()
except Exception as e:
    print(f"Word is not available: {e}")
    sys.exit(1)
