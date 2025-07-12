import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import logging

logger = logging.getLogger(__name__)


class CpuProfileWidget(Adw.ActionRow):
    """Widget for controlling CPU performance profiles"""
    
    def __init__(self, system_controller):
        super().__init__()
        self.system_controller = system_controller
        
        self.set_title("Performance Profile")
        self.set_subtitle("Control CPU performance mode")
        
        # Create dropdown for profile selection
        self.profile_dropdown = Gtk.DropDown()
        self.profile_dropdown.set_valign(Gtk.Align.CENTER)
        self.profile_dropdown.connect('notify::selected', self.on_profile_changed)
        
        self.add_suffix(self.profile_dropdown)
        
        # Load available profiles
        self.load_profiles()
        
    def load_profiles(self):
        """Load available CPU profiles"""
        try:
            profiles = self.system_controller.get_cpu_profiles()
            logger.info(f"Available CPU profiles: {profiles}")
            
            # Create string list model
            string_list = Gtk.StringList()
            for profile in profiles:
                string_list.append(profile)
                
            self.profile_dropdown.set_model(string_list)
            
            # Set current profile
            current_profile = self.system_controller.get_current_cpu_profile()
            logger.info(f"Current CPU profile: {current_profile}")
            
            if current_profile and current_profile in profiles:
                self.profile_dropdown.set_selected(profiles.index(current_profile))
            elif profiles:
                # If we can't get current profile, set to first available
                self.profile_dropdown.set_selected(0)
                
        except Exception as e:
            logger.error(f"Failed to load CPU profiles: {e}")
            self.set_subtitle(f"Error: {e}")
            
    def on_profile_changed(self, dropdown, param):
        """Handle profile selection change"""
        selected_index = dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = dropdown.get_model()
            profile = model.get_string(selected_index)
            
            # Set profile in background to avoid blocking UI
            GLib.idle_add(self.set_profile_async, profile)
            
    def set_profile_async(self, profile):
        """Set CPU profile asynchronously"""
        try:
            self.system_controller.set_cpu_profile(profile)
        except Exception as e:
            logger.error(f"Failed to set CPU profile: {e}")
        return False
        
    def load_current_state(self):
        """Load current CPU profile state"""
        self.load_profiles() 