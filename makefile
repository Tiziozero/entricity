.PHONY: server client

# Default to development mode if MODE is not specified
MODE ?= dev
SERVER_BIN := EntricityServer
SERVER_DIR := Server
CLIENT_DIR := Entricity

# Server target
server:
ifeq ($(MODE),release)
	@echo "Building and running the server (release version)..."
	# Add your commands for building and running the release server here
	cd $(SERVER_DIR) && go build -o server_binary
else
	@echo "Building and running the server (dev version)..."
	# Dev run server
	cd $(SERVER_DIR) && powershell.exe -Command "air -c .air.toml.win"
	# Server clean is handled by air... I think
endif

# Client target
client:
ifeq ($(MODE),release)
	@echo "Building and running the client (release version)..."
	# Add your commands for building and running the release client here
	cd $(CLIENT_DIR) && powershell.exe -File "psrun.ps1"
else
	@echo "Building and running the client (dev version)..."
	# Dev run client
	cd $(CLIENT_DIR) && powershell.exe -File "psrun.ps1"
	@echo "Cleaning client..."
	rm -f $(CLIENT_DIR)/client.log
	rm -rf $(CLIENT_DIR)/src/__pycache__
	rm -rf $(CLIENT_DIR)/__pycache__
endif
