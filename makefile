all: run clean

run:
	@echo "running ..."
	powershell.exe -File "psrun.ps1"

clean:
	@echo "Cleaning up..."
	rm -f client.log
	rm -rf src/__pycache__
