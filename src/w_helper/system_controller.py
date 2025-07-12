import subprocess
import logging
import re
import os
from typing import List, Dict, Optional, Tuple
from gi.repository import GObject

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
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
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
        # success, output = self.run_command(['asusctl', 'profile', '-l'], False)
        output = subprocess.run(['asusctl', 'profile', '-l'], capture_output=True, text=True, check=True).stdout
        print(output)
        # if not success:
        #     return ['Balanced', 'Performance', 'Quiet']  # Fallback
            
        profiles = []
        for line in output.split('\n'):
            if 'Starting' not in line:
                profiles.append(line)
        return profiles or []
        
    def get_current_cpu_profile(self) -> Optional[str]:
        """Get current CPU profile"""
        success, output = self.run_command(['asusctl', 'profile', '--p'], False)
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
        
    # GPU Mode Methods
    def get_gpu_modes(self) -> List[str]:
        """Get available GPU modes"""
        success, output = self.run_command(['supergfxctl', '--get-modes'], False)
        if not success:
            return ['Integrated', 'Hybrid', 'Discrete']  # Fallback
            
        modes = []
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('Available'):
                modes.append(line)
        return modes or ['Integrated', 'Hybrid', 'Discrete']
        
    def get_current_gpu_mode(self) -> Optional[str]:
        """Get current GPU mode"""
        success, output = self.run_command(['supergfxctl', '--get'], False)
        if not success:
            return None
        return output.strip()
        
    def set_gpu_mode(self, mode: str) -> bool:
        """Set GPU mode"""
        success, output = self.run_command(['supergfxctl', '--set-mode', mode], False)
        
        if success:
            self.emit('status-changed', 'gpu', f'GPU mode set to {mode} (restart may be required)', True)
        else:
            self.emit('status-changed', 'gpu', f'Failed to set GPU mode: {output}', False)
            
        return success
        
    # Display Methods
    def get_available_refresh_rates(self) -> List[str]:
        """Get available refresh rates"""
        success, output = self.run_command(['xrandr', '--query'], False)
        if not success:
            return ['60', '120', '165']  # Fallback
            
        rates = set()
        for line in output.split('\n'):
            if '*' in line or '+' in line:  # Current or preferred mode
                # Extract refresh rates from mode line
                matches = re.findall(r'(\d+\.\d+)', line)
                for match in matches:
                    rate = str(int(float(match)))
                    rates.add(rate)
                    
        return sorted(list(rates)) or ['60', '120', '165']
        
    def get_current_refresh_rate(self) -> Optional[str]:
        """Get current refresh rate"""
        success, output = self.run_command(['xrandr', '--query'], False)
        if not success:
            return None
            
        for line in output.split('\n'):
            if '*' in line:  # Current mode
                match = re.search(r'(\d+\.\d+)\*', line)
                if match:
                    return str(int(float(match.group(1))))
        return None
        
    def set_refresh_rate(self, rate: str) -> bool:
        """Set refresh rate"""
        # Get primary display
        success, output = self.run_command(['xrandr', '--query'], False)
        if not success:
            return False
            
        primary_display = None
        for line in output.split('\n'):
            if ' connected primary' in line:
                primary_display = line.split()[0]
                break
                
        if not primary_display:
            # Try to find any connected display
            for line in output.split('\n'):
                if ' connected' in line:
                    primary_display = line.split()[0]
                    break
                    
        if not primary_display:
            self.emit('status-changed', 'display', 'No connected display found', False)
            return False
            
        # Set refresh rate
        success, output = self.run_command([
            'xrandr', '--output', primary_display, '--rate', rate
        ], False)
        
        if success:
            self.emit('status-changed', 'display', f'Refresh rate set to {rate}Hz', True)
        else:
            self.emit('status-changed', 'display', f'Failed to set refresh rate: {output}', False)
            
        return success
        
    # Battery Methods
    def get_battery_charge_limit(self) -> Optional[int]:
        """Get current battery charge limit"""
        success, output = self.run_command(['asusctl', 'batt', '--get-charge-limit'], False)
        if not success:
            return None
            
        match = re.search(r'(\d+)', output)
        if match:
            return int(match.group(1))
        return None
        
    def set_battery_charge_limit(self, limit: int) -> bool:
        """Set battery charge limit"""
        success, output = self.run_command([
            'asusctl', 'batt', '--set-charge-limit', str(limit)
        ], False)
        
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