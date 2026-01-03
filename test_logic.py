from src.ram_cleaner import RamCleaner
from src.scanner import ScamScanner
import os

def test_ram_cleaner():
    print("Testing RAM Cleaner...")
    info = RamCleaner.get_memory_info()
    print(f"Initial Memory: {info}")
    
    cleaned = RamCleaner.clean_working_set()
    print(f"Cleaned {cleaned} processes.")
    
    info_after = RamCleaner.get_memory_info()
    print(f"Memory After: {info_after}")
    print("RAM Cleaner Test Passed")

def test_scanner():
    print("\nTesting Scanner...")
    scanner = ScamScanner()
    drives = scanner.get_drives()
    print(f"Drives found: {drives}")
    
    # Create a dummy download folder for testing
    test_dir = os.path.join(os.getcwd(), 'TestDownloads')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a dummy suspicious file
    with open(os.path.join(test_dir, 'suspicious.exe'), 'w') as f:
        f.write("fake exe")
        
    # Test scan
    print(f"Scanning test directory: {test_dir}")
    results = scanner.scan_folder(test_dir)
    print("Results:", results)
    
    assert len(results) == 1
    assert results[0]['name'] == 'suspicious.exe'
    
    # Cleanup
    os.remove(os.path.join(test_dir, 'suspicious.exe'))
    os.rmdir(test_dir)
    print("Scanner Test Passed")

if __name__ == "__main__":
    try:
        test_ram_cleaner()
        test_scanner()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
