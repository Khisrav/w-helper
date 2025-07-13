import json
import subprocess
import logging
import re
import os
from typing import List, Dict, Optional, Tuple
from gi.repository import GObject

try:
    from pydbus import SessionBus
    PYDBUS_AVAILABLE = True
except ImportError:
    PYDBUS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemController(GObject.Object):
    """Controller for system hardware interactions"""
    
    __gsignals__ = {
        'status-changed': (GObject.SignalFlags.RUN_FIRST, None, (str, str, bool))
    }
    
    def __init__(self):
        super().__init__()
        self.check_system_requirements()
        
    def check_system_requirements(self):
        """Check if required system utilities are available"""
        required_tools = {
            'asusctl': 'ASUS Control utility',
            'supergfxctl': 'SuperGFX Control utility',
            'xrandr': 'X11 display configuration',
        }
        
        missing_tools = []
        for tool, description in required_tools.items():
            if not self.command_exists(tool):
                missing_tools.append(f"{tool} ({description})")
                
        if missing_tools:
            logger.warning(f"Missing tools: {', '.join(missing_tools)}")
            
    def command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run(['which', command], check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def run_command(self, command: List[str], require_success: bool = True) -> Tuple[bool, str]:
        """Run a system command and return success status and output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,    
                text=True,
                check=require_success
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            logger.error(f"Command failed: {' '.join(command)}: {error_msg}")
            return False, error_msg
        except FileNotFoundError:
            error_msg = f"Command not found: {command[0]}"
            logger.error(error_msg)
            return False, error_msg
            
    # CPU Profile Methods
    def get_cpu_profiles(self) -> List[str]:
        """Get available CPU profiles"""
        success, output = self.run_command(['asusctl', 'profile', '-l'], False)
        if not success:
            raise RuntimeError(f"Failed to get CPU profiles: {output}")
            
        profiles = []
        for line in output.split('\n'):
            line = line.strip()
            if line and 'Starting' not in line:
                profiles.append(line)
        
        if not profiles:
            raise RuntimeError(f"No CPU profiles found in output: {repr(output)}")
            
        return profiles
        
    def get_current_cpu_profile(self) -> Optional[str]:
        """Get current CPU profile"""
        success, output = self.run_command(['asusctl', 'profile', '-p'], False)
        if not success:
            return None
            
        # Parse output to find current profile
        match = re.search(r'Active profile is\s*(\w+)', output)
        if match:
            return match.group(1)
        return None
        
    def set_cpu_profile(self, profile: str) -> bool:
        """Set CPU profile"""
        success, output = self.run_command(['asusctl', 'profile', '-P', profile], False)
        
        if success:
            self.emit('status-changed', 'cpu', f'CPU profile set to {profile}', True)
        else:
            self.emit('status-changed', 'cpu', f'Failed to set CPU profile: {output}', False)
            
        return success
        
    def get_gpu_modes(self) -> List[str]:
        """Get available GPU modes"""
        success, output = self.run_command(['supergfxctl', '-s'], False)
        if not success:
            raise RuntimeError(f"Failed to run 'supergfxctl -s': {output}")
    
        # Parse the output - it can be in different formats
        modes = []
        
        # Check if output looks like a list format: [Mode1, Mode2, Mode3]
        if output.startswith('[') and output.endswith(']'):
            # Remove brackets and split by comma
            content = output[1:-1]
            for item in content.split(','):
                mode = item.strip()
                if mode:
                    modes.append(mode)
        else:
            # Parse line by line for text format
            for line in output.split('\n'):
                line = line.strip()
                if line and not line.startswith('Available') and not line.startswith('Current'):
                    modes.append(line)
    
        if not modes:
            raise RuntimeError(f"No GPU modes found in supergfxctl output: {repr(output)}")
    
        return modes
        
    def get_current_gpu_mode(self) -> Optional[str]:
        """Get current GPU mode"""
        success, output = self.run_command(['supergfxctl', '--get'], False)
        if not success:
            return None
        return output.strip()
        
    def set_gpu_mode(self, mode: str) -> bool:
        """Set GPU mode"""
        success, output = self.run_command(['supergfxctl', '-m', mode], False)
        
        if success:
            self.emit('status-changed', 'gpu', f'GPU mode set to {mode} (restart may be required)', True)
        else:
            self.emit('status-changed', 'gpu', f'Failed to set GPU mode: {output}', False)
            
        return success
        
    # Display Methods
    def get_available_refresh_rates(self) -> List[str]:
        """Get available refresh rates using GNOME DisplayConfig D-Bus interface"""
        if not PYDBUS_AVAILABLE:
            raise RuntimeError("pydbus is required for display configuration")
            
        try:
            bus = SessionBus()
            display_config = bus.get("org.gnome.Mutter.DisplayConfig")
            
            # Get current display config
            serial, monitors, logical_monitors, properties = display_config.GetCurrentState()
            
            rates = set()
            for monitor in monitors:
                for mode in monitor[1]:  # modes are in the second element
                    refresh = mode[3]  # refresh rate is at index 3
                    rates.add(str(int(refresh)))
                    
            if not rates:
                raise RuntimeError("No refresh rates found")
                
            return sorted(list(rates))
            
        except Exception as e:
            raise RuntimeError(f"Failed to get refresh rates via D-Bus: {e}")
        
    def get_current_refresh_rate(self) -> Optional[str]:
        """Get current refresh rate using GNOME DisplayConfig D-Bus interface"""
        if not PYDBUS_AVAILABLE:
            return None
            
        try:
            bus = SessionBus()
            display_config = bus.get("org.gnome.Mutter.DisplayConfig")
            
            # Get current display config
            serial, monitors, logical_monitors, properties = display_config.GetCurrentState()
            
            # Find the current mode for the primary monitor
            for monitor in monitors:
                for mode in monitor[1]:  # modes
                    if len(mode) > 6 and isinstance(mode[6], dict) and mode[6].get('is-current', False):
                        refresh = mode[3]  # refresh rate is at index 3
                        return str(int(refresh))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get current refresh rate: {e}")
            return None
        
    def set_refresh_rate(self, rate: str) -> bool:
        """Set refresh rate using GNOME DisplayConfig D-Bus interface"""
        if not PYDBUS_AVAILABLE:
            self.emit('status-changed', 'display', 'pydbus is required for display configuration', False)
            return False
            
        self.emit('status-changed', 'display', 
                 f'Refresh rate setting to {rate}Hz is not yet implemented. '
                 f'Please use your system settings.', False)
        return False
        
    # Battery Methods
    def get_battery_charge_limit(self) -> Optional[int]:
        """Get current battery charge limit"""
        try:
            with open('/sys/class/power_supply/BAT0/charge_control_end_threshold', 'r') as f:
                return int(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read charge limit: {e}")
            return None
        
    def set_battery_charge_limit(self, limit: int) -> bool:
        """Set battery charge limit"""
        success, output = self.run_command(['asusctl', '-c', str(limit)], False)
        
        if success:
            self.emit('status-changed', 'battery', f'Battery charge limit set to {limit}%', True)
        else:
            self.emit('status-changed', 'battery', f'Failed to set battery limit: {output}', False)
            
        return success
        
    def get_battery_info(self) -> Dict[str, str]:
        """Get battery information"""
        info = {}
        
        # Try to get battery info from power supply
        battery_path = '/sys/class/power_supply/BAT0'
        if os.path.exists(battery_path):
            try:
                with open(f'{battery_path}/capacity', 'r') as f:
                    info['capacity'] = f.read().strip() + '%'
                with open(f'{battery_path}/status', 'r') as f:
                    info['status'] = f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to read battery info: {e}")
                
        return info 