.PHONY: all clean build server client clean_server clean_client

# Variables for server and client directories
SERVER_DIR := Server
CLIENT_DIR := Entricity

# Default target
all: build

# Build targets
build: build_server build_client

build_server:
	@echo "Building server..."
	
	cd $(SERVER_DIR) && go run .
	# cd $(SERVER_DIR) && air


run_client:
	@echo "Running client..."
	cd $(CLIENT_DIR) && powershell.exe -File "psrun.ps1"

# Clean targets
clean: clean_server clean_client

clean_server:
	@echo "Cleaning server..."
	# rm -f $(SERVER_DIR)/$(SERVER_BINARY) # Adjust this line based on how your server binary is named or stored

clean_client:
	@echo "Cleaning client..."
	rm -f $(CLIENT_DIR)/client.log
	rm -rf $(CLIENT_DIR)/src/__pycache__

# Running targets
server: build_server
	@echo "Starting server..."
	# cd $(SERVER_DIR) && ./$(SERVER_BINARY) # Ensure SERVER_BINARY is defined appropriately

client: run_client

# Optional: Define the server binary name if needed
# SERVER_BINARY := server_binary_name # Replace with actual server binary name if necessary

