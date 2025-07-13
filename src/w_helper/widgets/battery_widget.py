import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import logging

logger = logging.getLogger(__name__)


class BatteryWidget(Adw.PreferencesGroup):
    """Widget for controlling battery settings"""
    
    def __init__(self, system_controller):
        super().__init__()
        self.system_controller = system_controller
        
        # self.set_title("Battery Control")
        # self.set_description("Control battery charging behavior")
        
        # Battery info row
        self.info_row = Adw.ActionRow()
        self.info_row.set_title("Battery Status")
        self.info_row.set_subtitle("Loading...")
        
        # Battery icon
        self.battery_icon = Gtk.Image()
        self.battery_icon.set_from_icon_name("battery-symbolic")
        self.info_row.add_prefix(self.battery_icon)
        
        self.add(self.info_row)
        
        # Charge limit row
        self.limit_row = Adw.ActionRow()
        self.limit_row.set_title("Charge Limit")
        self.limit_row.set_subtitle("Set maximum battery charge percentage")
        
        # Charge limit scale
        self.limit_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 60, 100, 5
        )
        self.limit_scale.set_digits(0)
        self.limit_scale.set_value(100)
        self.limit_scale.set_hexpand(True)
        self.limit_scale.set_valign(Gtk.Align.CENTER)
        self.limit_scale.connect('value-changed', self.on_limit_changed)
        
        # Add marks for common values
        self.limit_scale.add_mark(60, Gtk.PositionType.BOTTOM, "60%")
        self.limit_scale.add_mark(80, Gtk.PositionType.BOTTOM, "80%")
        self.limit_scale.add_mark(100, Gtk.PositionType.BOTTOM, "100%")
        
        self.limit_row.add_suffix(self.limit_scale)
        self.add(self.limit_row)
        
        # Load current state
        self.load_battery_info()
        self.load_charge_limit()
        
    def load_battery_info(self):
        """Load current battery information"""
        try:
            info = self.system_controller.get_battery_info()
            
            if info:
                capacity = info.get('capacity', 'Unknown')
                status = info.get('status', 'Unknown')
                
                subtitle = f"{capacity} - {status}"
                self.info_row.set_subtitle(subtitle)
                
                # Update battery icon based on status
                if status.lower() == 'charging':
                    self.battery_icon.set_from_icon_name("battery-charging-symbolic")
                elif status.lower() == 'discharging':
                    self.battery_icon.set_from_icon_name("battery-symbolic")
                elif status.lower() == 'full':
                    self.battery_icon.set_from_icon_name("battery-full-symbolic")
                else:
                    self.battery_icon.set_from_icon_name("battery-symbolic")
            else:
                self.info_row.set_subtitle("Battery information not available")
                
        except Exception as e:
            logger.error(f"Failed to load battery info: {e}")
            self.info_row.set_subtitle(f"Error: {e}")
            
    def load_charge_limit(self):
        """Load current charge limit"""
        try:
            limit = self.system_controller.get_battery_charge_limit()
            if limit is not None:
                self.limit_scale.set_value(limit)
            else:
                self.limit_row.set_subtitle("Charge limit control not available")
                self.limit_scale.set_sensitive(False)
                
        except Exception as e:
            logger.error(f"Failed to load charge limit: {e}")
            self.limit_row.set_subtitle(f"Error: {e}")
            self.limit_scale.set_sensitive(False)
            
    def on_limit_changed(self, scale):
        """Handle charge limit change"""
        limit = int(scale.get_value())
        
        # Update subtitle to show current value
        self.limit_row.set_subtitle(f"Current limit: {limit}%")
        
        # Set limit in background to avoid blocking UI
        GLib.idle_add(self.set_limit_async, limit)
        
    def set_limit_async(self, limit):
        """Set charge limit asynchronously"""
        try:
            self.system_controller.set_battery_charge_limit(limit)
        except Exception as e:
            logger.error(f"Failed to set charge limit: {e}")
        return False
        
    def load_current_state(self):
        """Load current battery state"""
        self.load_battery_info()
        self.load_charge_limit()
        
        # Refresh battery info periodically
        GLib.timeout_add_seconds(30, self.refresh_battery_info)
        
    def refresh_battery_info(self):
        """Refresh battery information"""
        self.load_battery_info()
        return True  # Continue periodic refresh 