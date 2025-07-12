import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio
import logging

from .widgets.cpu_profile_widget import CpuProfileWidget
from .widgets.gpu_mode_widget import GpuModeWidget
from .widgets.refresh_rate_widget import RefreshRateWidget
from .widgets.battery_widget import BatteryWidget


class WHelperWindow(Adw.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, application, system_controller):
        super().__init__(application=application)
        
        self.system_controller = system_controller
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        self.set_title("W-Helper")
        self.set_default_size(400, 600)
        
        # Create main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Create toolbar view (AdwApplicationWindow way)
        toolbar_view = Adw.ToolbarView()
        
        # Create header bar
        header_bar = Adw.HeaderBar()
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(self.create_menu())
        header_bar.pack_end(menu_button)
        
        # Add header bar to toolbar view
        toolbar_view.add_top_bar(header_bar)
        
        # Scroll container
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Set scrolled window as content of toolbar view
        toolbar_view.set_content(scrolled)
        
        # Set the main content
        self.set_content(toolbar_view)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(24)
        content_box.set_margin_end(24)
        scrolled.set_child(content_box)
        
        # System status banner
        self.status_banner = Adw.Banner()
        self.status_banner.set_revealed(False)
        content_box.append(self.status_banner)
        
        # CPU Profile Section
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("CPU Performance")
        cpu_group.set_description("Control CPU performance profiles")
        
        self.cpu_widget = CpuProfileWidget(self.system_controller)
        cpu_group.add(self.cpu_widget)
        content_box.append(cpu_group)
        
        # GPU Mode Section
        gpu_group = Adw.PreferencesGroup()
        gpu_group.set_title("GPU Mode")
        gpu_group.set_description("Switch between integrated and discrete GPU")
        
        self.gpu_widget = GpuModeWidget(self.system_controller)
        gpu_group.add(self.gpu_widget)
        content_box.append(gpu_group)
        
        # Display Section
        display_group = Adw.PreferencesGroup()
        display_group.set_title("Display")
        display_group.set_description("Control display refresh rate")
        
        self.refresh_widget = RefreshRateWidget(self.system_controller)
        display_group.add(self.refresh_widget)
        content_box.append(display_group)
        
        # Battery Section
        battery_group = Adw.PreferencesGroup()
        battery_group.set_title("Battery")
        battery_group.set_description("Control battery charging behavior")
        
        self.battery_widget = BatteryWidget(self.system_controller)
        battery_group.add(self.battery_widget)
        content_box.append(battery_group)
        
        # Connect signals
        self.connect_signals()
        
        # Initial load
        self.load_initial_state()
        
    def create_menu(self):
        """Create the application menu"""
        menu = Gio.Menu()
        menu.append("About W-Helper", "app.about")
        menu.append("Quit", "app.quit")
        return menu
        
    def connect_signals(self):
        """Connect widget signals"""
        # Connect to system controller status updates
        self.system_controller.connect('status-changed', self.on_status_changed)
        
    def on_status_changed(self, controller, status_type, message, success):
        """Handle status changes from system controller"""
        if success:
            self.status_banner.set_title(f"✓ {message}")
            self.status_banner.add_css_class("success")
        else:
            self.status_banner.set_title(f"⚠ {message}")
            self.status_banner.add_css_class("error")
            
        self.status_banner.set_revealed(True)
        
        # Auto-hide after 3 seconds
        GLib.timeout_add_seconds(3, self.hide_status_banner)
        
    def hide_status_banner(self):
        """Hide the status banner"""
        self.status_banner.set_revealed(False)
        self.status_banner.remove_css_class("success")
        self.status_banner.remove_css_class("error")
        return False
        
    def load_initial_state(self):
        """Load initial system state"""
        try:
            logging.info("Loading initial system state...")
            # Load current states for all widgets
            self.cpu_widget.load_current_state()
            self.gpu_widget.load_current_state()
            self.refresh_widget.load_current_state()
            self.battery_widget.load_current_state()
            logging.info("Initial system state loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load initial state: {e}")
            self.on_status_changed(None, "error", f"Failed to load system state: {e}", False) 