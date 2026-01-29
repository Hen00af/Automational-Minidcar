
import os
import sys

def check_environment():
    print("=== Environment Check ===")
    
    # 1. Check OS/Platform details
    print(f"Platform: {sys.platform}")
    
    # 2. Check /proc/cpuinfo for Raspberry Pi indicators
    is_pi = False
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                print("Hardware: Raspberry Pi / BCM detected in cpuinfo")
                is_pi = True
            else:
                print("Hardware: No Raspberry Pi indicators found in cpuinfo")
    except Exception as e:
        print(f"Hardware: Could not read /proc/cpuinfo: {e}")

    # 3. Check environment variables
    use_mock = os.environ.get('USE_MOCK_HARDWARE')
    print(f"USE_MOCK_HARDWARE env var: {use_mock}")

    # 4. Import hardware_import logic
    sys.path.append(os.getcwd())
    try:
        # Assuming we are in the project root or test_code dir needs to be in path
        if os.path.exists('test_code'):
             sys.path.append(os.path.join(os.getcwd(), 'test_code'))
        
        import hardware_import
        print(f"hardware_import.is_raspberry_pi() returns: {hardware_import.is_raspberry_pi()}")
        
        # Check what modules are loaded
        if hasattr(hardware_import, 'board'):
            print(f"Loaded 'board' module: {hardware_import.board}")
        
    except ImportError as e:
        print(f"Could not import hardware_import: {e}")
    except Exception as e:
        print(f"Error checking hardware_import: {e}")

    if not is_pi:
        print("\n[CONCLUSION]")
        print("This environment is NOT recognized as a Raspberry Pi.")
        print("The system is running with MOCK hardware modules.")
        print("Real motors and servos WILL NOT MOVE.")
    else:
        print("\n[CONCLUSION]")
        print("This environment IS recognized as a Raspberry Pi.")

if __name__ == "__main__":
    check_environment()
