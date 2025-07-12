#!/usr/bin/env python3
"""
Test script to verify W-Helper installation
"""

import sys
import subprocess
import os

def test_python_imports():
    """Test Python imports"""
    print("🧪 Testing Python imports...")
    
    try:
        from w_helper.system_controller import SystemController
        print("✅ SystemController imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SystemController: {e}")
        return False
    
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_version('Adw', '1')
        from gi.repository import Gtk, Adw
        print("✅ GTK 4 and libadwaita available")
    except ImportError as e:
        print(f"❌ GTK/libadwaita not available: {e}")
        return False
    
    return True

def test_system_utilities():
    """Test system utilities availability"""
    print("\n🔧 Testing system utilities...")
    
    utilities = {
        'asusctl': 'ASUS Control utility',
        'supergfxctl': 'SuperGFX Control utility',
        'xrandr': 'X11 display configuration'
    }
    
    all_available = True
    for util, desc in utilities.items():
        try:
            subprocess.run(['which', util], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ {util} ({desc}) available")
        except subprocess.CalledProcessError:
            print(f"⚠️  {util} ({desc}) not found")
            all_available = False
    
    return all_available

def test_services():
    """Test ASUS services status"""
    print("\n🔧 Testing ASUS services...")
    
    services = ['asusd', 'supergfxd']
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'is-active', service], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {service} is running")
            else:
                print(f"⚠️  {service} is not running")
        except Exception as e:
            print(f"❌ Error checking {service}: {e}")

def test_cli_commands():
    """Test CLI commands"""
    print("\n💻 Testing CLI commands...")
    
    try:
        # Test if w-helper command exists
        result = subprocess.run(['w-helper', '--help'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ w-helper CLI command working")
        else:
            print("❌ w-helper CLI command failed")
    except FileNotFoundError:
        print("❌ w-helper command not found in PATH")
    
    # Test Python module execution
    try:
        result = subprocess.run([sys.executable, '-m', 'w_helper.cli', '--help'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Python module execution working")
        else:
            print("❌ Python module execution failed")
    except Exception as e:
        print(f"❌ Python module execution error: {e}")

def test_desktop_integration():
    """Test desktop integration"""
    print("\n🖥️  Testing desktop integration...")
    
    desktop_file = os.path.expanduser('~/.local/share/applications/w-helper.desktop')
    if os.path.exists(desktop_file):
        print("✅ Desktop entry installed")
    else:
        print("❌ Desktop entry not found")

def main():
    """Main test function"""
    print("🚀 W-Helper Installation Test")
    print("=" * 40)
    
    success = True
    
    # Test Python imports
    if not test_python_imports():
        success = False
    
    # Test system utilities
    if not test_system_utilities():
        print("\n⚠️  Some system utilities are missing. Install them with:")
        print("   sudo dnf install -y asusctl supergfxctl")
        success = False
    
    # Test services
    test_services()
    
    # Test CLI commands
    test_cli_commands()
    
    # Test desktop integration
    test_desktop_integration()
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 W-Helper installation test completed successfully!")
        print("\nYou can now:")
        print("  • Run 'w-helper-gui' to launch the GUI")
        print("  • Run 'w-helper status' to check system status")
        print("  • Launch from your application menu")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 