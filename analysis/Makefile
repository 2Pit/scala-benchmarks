VENV_DIR := venv

.PHONY: init run update

init:
	python3 -m venv venv

run:
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV_DIR)/bin/activate"

# Install dependencies with OpenBLAS-related environment variables
update:
	@echo "Installing requirements with OpenBLAS support..."
	@. $(VENV_DIR)/bin/activate && \
	LDFLAGS="-L/opt/homebrew/opt/openblas/lib" \
	CPPFLAGS="-I/opt/homebrew/opt/openblas/include" \
	PKG_CONFIG_PATH="/opt/homebrew/opt/openblas/lib/pkgconfig" \
	pip install -r requirements.txt
