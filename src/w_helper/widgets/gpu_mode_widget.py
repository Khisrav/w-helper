import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import logging

logger = logging.getLogger(__name__)


class GpuModeWidget(Adw.ActionRow):
    """Widget for controlling GPU mode"""
    
    def __init__(self, system_controller):
        super().__init__()
        self.system_controller = system_controller
        
        self.set_title("GPU Mode")
        self.set_subtitle("Switch between integrated and discrete GPU")
        
        # Create dropdown for GPU mode selection
        self.mode_dropdown = Gtk.DropDown()
        self.mode_dropdown.set_valign(Gtk.Align.CENTER)
        self.mode_dropdown.connect('notify::selected', self.on_mode_changed)
        
        self.add_suffix(self.mode_dropdown)
        
        # Warning label for restart requirement
        self.warning_label = Gtk.Label()
        self.warning_label.set_text("⚠ Restart required after change")
        self.warning_label.add_css_class("warning")
        self.warning_label.set_visible(False)
        
        # Add warning to a box
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        warning_box.append(self.warning_label)
        self.add_suffix(warning_box)
        
        # Load available modes
        self.load_modes()
        
    def load_modes(self):
        """Load available GPU modes"""
        try:
            modes = self.system_controller.get_gpu_modes()
            logger.info(f"Available GPU modes: {modes}")
            
            # Create string list model
            string_list = Gtk.StringList()
            for mode in modes:
                string_list.append(mode)
                
            self.mode_dropdown.set_model(string_list)
            
            # Set current mode
            current_mode = self.system_controller.get_current_gpu_mode()
            logger.info(f"Current GPU mode: {current_mode}")
            
            if current_mode and current_mode in modes:
                self.mode_dropdown.set_selected(modes.index(current_mode))
            elif modes:
                # If we can't get current mode, set to first available
                self.mode_dropdown.set_selected(0)
                
        except Exception as e:
            logger.error(f"Failed to load GPU modes: {e}")
            self.set_subtitle(f"Error: {e}")
            
    def on_mode_changed(self, dropdown, param):
        """Handle GPU mode selection change"""
        selected_index = dropdown.get_selected()
        if selected_index != Gtk.INVALID_LIST_POSITION:
            model = dropdown.get_model()
            mode = model.get_string(selected_index)
            
            # Set mode in background to avoid blocking UI
            GLib.idle_add(self.set_mode_async, mode)
            
    def set_mode_async(self, mode):
        """Set GPU mode asynchronously"""
        try:
            success = self.system_controller.set_gpu_mode(mode)
            if success:
                # Show restart warning
                self.warning_label.set_visible(True)
                # Hide warning after 10 seconds
                GLib.timeout_add_seconds(10, self.hide_warning)
        except Exception as e:
            logger.error(f"Failed to set GPU mode: {e}")
        return False
        
    def hide_warning(self):
        """Hide the restart warning"""
        self.warning_label.set_visible(False)
        return False
        
    def load_current_state(self):
        """Load current GPU mode state"""
        self.load_modes() 