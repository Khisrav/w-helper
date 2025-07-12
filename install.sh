#!/bin/bash

# W-Helper Installation Script for Fedora 42
# This script installs W-Helper and its dependencies

set -e

echo "🔧 Installing W-Helper for ASUS ROG Zephyrus G14..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-gobject \
    gtk4 \
    libadwaita \
    python3-gobject-devel \
    pkg-config \
    gcc \
    glib2-devel \
    gtk4-devel \
    libadwaita-devel \
    cairo-devel \
    cairo-gobject-devel

# Install ASUS control utilities
echo "📦 Installing ASUS control utilities..."
sudo dnf install -y asusctl supergfxctl

# Enable and start services
echo "🔧 Enabling ASUS services..."
sudo systemctl enable --now asusd
sudo systemctl enable --now supergfxd

# Install W-Helper
echo "📦 Installing W-Helper..."
pip3 install --user .

# Install desktop entry
echo "📦 Installing desktop entry..."
mkdir -p ~/.local/share/applications
cp w-helper.desktop ~/.local/share/applications/

# Update desktop database
echo "📦 Updating desktop database..."
update-desktop-database ~/.local/share/applications/

# Add user to necessary groups
echo "👤 Adding user to necessary groups..."
sudo usermod -a -G wheel "$USER"

echo "✅ W-Helper installation completed!"
echo ""
echo "🎉 You can now:"
echo "   • Launch W-Helper from your application menu"
echo "   • Run 'w-helper-gui' from the terminal"
echo "   • Use 'w-helper --help' for command line options"
echo ""
echo "📋 Note: You may need to log out and log back in for group changes to take effect"
echo "🔄 If you encounter permission issues, try rebooting your system" 