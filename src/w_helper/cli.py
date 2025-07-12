#!/usr/bin/env python3

import argparse
import sys
from .system_controller import SystemController


def main():
    """Command line interface for W-Helper"""
    parser = argparse.ArgumentParser(
        description="W-Helper - ASUS ROG Zephyrus G14 Control Center for Linux"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # CPU profile commands
    cpu_parser = subparsers.add_parser('cpu', help='CPU profile control')
    cpu_subparsers = cpu_parser.add_subparsers(dest='cpu_action')
    
    cpu_subparsers.add_parser('list', help='List available CPU profiles')
    cpu_subparsers.add_parser('get', help='Get current CPU profile')
    cpu_set_parser = cpu_subparsers.add_parser('set', help='Set CPU profile')
    cpu_set_parser.add_argument('profile', help='Profile name (e.g., Balanced, Performance, Quiet)')
    
    # GPU mode commands
    gpu_parser = subparsers.add_parser('gpu', help='GPU mode control')
    gpu_subparsers = gpu_parser.add_subparsers(dest='gpu_action')
    
    gpu_subparsers.add_parser('list', help='List available GPU modes')
    gpu_subparsers.add_parser('get', help='Get current GPU mode')
    gpu_set_parser = gpu_subparsers.add_parser('set', help='Set GPU mode')
    gpu_set_parser.add_argument('mode', help='GPU mode (e.g., Integrated, Hybrid, Discrete)')
    
    # Display commands
    display_parser = subparsers.add_parser('display', help='Display control')
    display_subparsers = display_parser.add_subparsers(dest='display_action')
    
    display_subparsers.add_parser('list', help='List available refresh rates')
    display_subparsers.add_parser('get', help='Get current refresh rate')
    display_set_parser = display_subparsers.add_parser('set', help='Set refresh rate')
    display_set_parser.add_argument('rate', help='Refresh rate in Hz (e.g., 60, 120, 165)')
    
    # Battery commands
    battery_parser = subparsers.add_parser('battery', help='Battery control')
    battery_subparsers = battery_parser.add_subparsers(dest='battery_action')
    
    battery_subparsers.add_parser('info', help='Get battery information')
    battery_subparsers.add_parser('get-limit', help='Get current charge limit')
    battery_set_parser = battery_subparsers.add_parser('set-limit', help='Set charge limit')
    battery_set_parser.add_argument('limit', type=int, help='Charge limit percentage (60-100)')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # GUI command
    subparsers.add_parser('gui', help='Launch GUI interface')
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return 0
    
    # Launch GUI
    if args.command == 'gui':
        from .main import main as gui_main
        return gui_main()
    
    # Create system controller
    try:
        controller = SystemController()
    except Exception as e:
        print(f"❌ Error initializing system controller: {e}")
        return 1
    
    # Handle CPU commands
    if args.command == 'cpu':
        return handle_cpu_command(controller, args)
    
    # Handle GPU commands
    elif args.command == 'gpu':
        return handle_gpu_command(controller, args)
    
    # Handle display commands
    elif args.command == 'display':
        return handle_display_command(controller, args)
    
    # Handle battery commands
    elif args.command == 'battery':
        return handle_battery_command(controller, args)
    
    # Handle status command
    elif args.command == 'status':
        return handle_status_command(controller)
    
    return 0


def handle_cpu_command(controller, args):
    """Handle CPU profile commands"""
    if args.cpu_action == 'list':
        profiles = controller.get_cpu_profiles()
        print("Available CPU profiles:")
        for profile in profiles:
            print(f"  • {profile}")
    
    elif args.cpu_action == 'get':
        profile = controller.get_current_cpu_profile()
        if profile:
            print(f"Current CPU profile: {profile}")
        else:
            print("❌ Could not get current CPU profile")
            return 1
    
    elif args.cpu_action == 'set':
        success = controller.set_cpu_profile(args.profile)
        if success:
            print(f"✅ CPU profile set to {args.profile}")
        else:
            print(f"❌ Failed to set CPU profile to {args.profile}")
            return 1
    
    return 0


def handle_gpu_command(controller, args):
    """Handle GPU mode commands"""
    if args.gpu_action == 'list':
        modes = controller.get_gpu_modes()
        print("Available GPU modes:")
        for mode in modes:
            print(f"  • {mode}")
    
    elif args.gpu_action == 'get':
        mode = controller.get_current_gpu_mode()
        if mode:
            print(f"Current GPU mode: {mode}")
        else:
            print("❌ Could not get current GPU mode")
            return 1
    
    elif args.gpu_action == 'set':
        success = controller.set_gpu_mode(args.mode)
        if success:
            print(f"✅ GPU mode set to {args.mode}")
            print("🔄 Restart required for changes to take effect")
        else:
            print(f"❌ Failed to set GPU mode to {args.mode}")
            return 1
    
    return 0


def handle_display_command(controller, args):
    """Handle display commands"""
    if args.display_action == 'list':
        rates = controller.get_available_refresh_rates()
        print("Available refresh rates:")
        for rate in rates:
            print(f"  • {rate}Hz")
    
    elif args.display_action == 'get':
        rate = controller.get_current_refresh_rate()
        if rate:
            print(f"Current refresh rate: {rate}Hz")
        else:
            print("❌ Could not get current refresh rate")
            return 1
    
    elif args.display_action == 'set':
        success = controller.set_refresh_rate(args.rate)
        if success:
            print(f"✅ Refresh rate set to {args.rate}Hz")
        else:
            print(f"❌ Failed to set refresh rate to {args.rate}Hz")
            return 1
    
    return 0


def handle_battery_command(controller, args):
    """Handle battery commands"""
    if args.battery_action == 'info':
        info = controller.get_battery_info()
        if info:
            print("Battery Information:")
            for key, value in info.items():
                print(f"  {key.capitalize()}: {value}")
        else:
            print("❌ Could not get battery information")
            return 1
    
    elif args.battery_action == 'get-limit':
        limit = controller.get_battery_charge_limit()
        if limit is not None:
            print(f"Current charge limit: {limit}%")
        else:
            print("❌ Could not get battery charge limit")
            return 1
    
    elif args.battery_action == 'set-limit':
        if args.limit < 60 or args.limit > 100:
            print("❌ Charge limit must be between 60 and 100")
            return 1
        
        success = controller.set_battery_charge_limit(args.limit)
        if success:
            print(f"✅ Battery charge limit set to {args.limit}%")
        else:
            print(f"❌ Failed to set battery charge limit to {args.limit}%")
            return 1
    
    return 0


def handle_status_command(controller):
    """Handle status command"""
    print("W-Helper System Status")
    print("=====================")
    
    # CPU Profile
    try:
        cpu_profile = controller.get_current_cpu_profile()
        print(f"CPU Profile: {cpu_profile if cpu_profile else 'Unknown'}")
    except Exception as e:
        print(f"CPU Profile: Error - {e}")
    
    # GPU Mode
    try:
        gpu_mode = controller.get_current_gpu_mode()
        print(f"GPU Mode: {gpu_mode if gpu_mode else 'Unknown'}")
    except Exception as e:
        print(f"GPU Mode: Error - {e}")
    
    # Display
    try:
        refresh_rate = controller.get_current_refresh_rate()
        print(f"Refresh Rate: {refresh_rate + 'Hz' if refresh_rate else 'Unknown'}")
    except Exception as e:
        print(f"Refresh Rate: Error - {e}")
    
    # Battery
    try:
        battery_info = controller.get_battery_info()
        if battery_info:
            capacity = battery_info.get('capacity', 'Unknown')
            status = battery_info.get('status', 'Unknown')
            print(f"Battery: {capacity} ({status})")
        else:
            print("Battery: Unknown")
    except Exception as e:
        print(f"Battery: Error - {e}")
    
    try:
        charge_limit = controller.get_battery_charge_limit()
        print(f"Charge Limit: {charge_limit}%" if charge_limit else "Charge Limit: Unknown")
    except Exception as e:
        print(f"Charge Limit: Error - {e}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 