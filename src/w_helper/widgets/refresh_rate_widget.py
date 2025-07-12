import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import logging

logger = logging.getLogger(__name__)


class RefreshRateWidget(Adw.ActionRow):
    """Widget for controlling display refresh rate"""
    
    def __init__(self, system_controller):
        super().__init__()
        self.system_controller = system_controller
        
        self.set_title("Refresh Rate")
        self.set_subtitle("Control display refresh rate")
        
        # Create dropdown for refresh rate selection
        self.rate_dropdown = Gtk.DropDown()
        self.rate_dropdown.set_valign(Gtk.Align.CENTER)
        self.rate_dropdown.connect('notify::selected', self.on_rate_changed)
        
        self.add_suffix(self.rate_dropdown)
        
        # Load available refresh rates
        self.load_refresh_rates()
        
    def load_refresh_rates(self):
        """Load available refresh rates"""
        try:
            rates = self.system_controller.get_available_refresh_rates()
            logger.info(f"Available refresh rates: {rates}")
            
            # Create string list model with Hz suffix
            string_list = Gtk.StringList()
            for rate in rates:
                string_list.append(f"{rate}Hz")
                
            self.rate_dropdown.set_model(string_list)
            
            # Set current refresh rate
            current_rate = self.system_controller.get_current_refresh_rate()
            logger.info(f"Current refresh rate: {current_rate}")
            
            if current_rate and current_rate in rates:
                self.rate_dropdown.set_selected(rates.index(current_rate))
            elif rates:
                # If we can't get current rate, set to first available
                self.rate_dropdown.set_selected(0)
                
        except Exception as e:
            logger.error(f"Failed to load refresh rates: {e}")
            self.set_subtitle(f"Error: {e}")
            
    def on_rate_changed(self, dropdown, param):
        """Handle refresh rate selection change"""
        selected_index = dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = dropdown.get_model()
            rate_text = model.get_string(selected_index)
            # Extract numeric value (remove "Hz" suffix)
            rate = rate_text.replace('Hz', '')
            
            # Set refresh rate in background to avoid blocking UI
            GLib.idle_add(self.set_rate_async, rate)
            
    def set_rate_async(self, rate):
        """Set refresh rate asynchronously"""
        try:
            self.system_controller.set_refresh_rate(rate)
        except Exception as e:
            logger.error(f"Failed to set refresh rate: {e}")
        return False
        
    def load_current_state(self):
        """Load current refresh rate state"""
        self.load_refresh_rates() 