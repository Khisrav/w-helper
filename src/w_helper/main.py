#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio
import sys
import os
import argparse
import logging

from .window import WHelperWindow
from .system_controller import SystemController


class WHelperApplication(Adw.Application):
    """Main application class for W-Helper"""
    
    def __init__(self):
        super().__init__(application_id='com.github.w-helper',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.system_controller = SystemController()
        self.window = None
        
    def do_activate(self):
        """Called when the application is activated"""
        if not self.window:
            self.window = WHelperWindow(
                application=self,
                system_controller=self.system_controller
            )
        
        self.window.present()
        
    def do_startup(self):
        """Called when the application starts"""
        Adw.Application.do_startup(self)
        
        # Create actions
        self.create_action('quit', self.quit_app)
        self.create_action('about', self.show_about)
        
        # Set up keyboard shortcuts
        self.set_accels_for_action('app.quit', ['<Control>q'])
        
    def create_action(self, name, callback):
        """Create an application action"""
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        
    def quit_app(self, action=None, param=None):
        """Quit the application"""
        self.quit()
        
    def show_about(self, action=None, param=None):
        """Show about dialog"""
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name="W-Helper",
            application_icon="application-x-executable",
            developer_name="W-Helper Team",
            version="0.1.0",
            description="ASUS ROG Zephyrus G14 Control Center for Linux",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/your-username/w-helper"
        )
        about.present()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="W-Helper - ASUS ROG Zephyrus G14 Control Center GUI"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='W-Helper 0.1.0'
    )
    
    return parser.parse_args()


def setup_logging(debug=False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    # Create and run the application
    app = WHelperApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    main() 