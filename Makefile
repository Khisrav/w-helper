# W-Helper Makefile
# Make commands for development and installation

.PHONY: help install dev-install test run clean uninstall

help:
	@echo "W-Helper - ASUS ROG Zephyrus G14 Control Center"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install W-Helper and dependencies"
	@echo "  dev-install - Install in development mode"
	@echo "  test        - Run tests and verify installation"
	@echo "  run         - Run the application"
	@echo "  clean       - Clean build artifacts"
	@echo "  uninstall   - Uninstall W-Helper"

install:
	@echo "🔧 Installing W-Helper..."
	chmod +x install.sh
	./install.sh

dev-install:
	@echo "🔧 Installing W-Helper in development mode..."
	pip3 install --user -e .

test:
	@echo "🧪 Testing W-Helper installation..."
	python3 -c "from w_helper.system_controller import SystemController; print('✅ SystemController imported successfully')"
	python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); print('✅ GTK 4 and libadwaita available')"
	w-helper --help > /dev/null && echo "✅ CLI command working" || echo "❌ CLI command not found"

run:
	@echo "🚀 Running W-Helper..."
	python3 -m w_helper.main

run-cli:
	@echo "🚀 Running W-Helper CLI..."
	python3 -m w_helper.cli

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

uninstall:
	@echo "🗑️  Uninstalling W-Helper..."
	pip3 uninstall -y w-helper
	rm -f ~/.local/share/applications/w-helper.desktop
	update-desktop-database ~/.local/share/applications/ 