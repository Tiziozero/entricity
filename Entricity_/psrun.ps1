# MyFirstScript.ps1
$source = ".\src\main.py"
$pyFlags = ""
$venv = "..\evenv"
$requirements = "requirements.txt"


$activatePath = ".\$venv\Scripts\activate"

# Check if venv exists

if (-Not (Test-Path -Path ".\$venv")) {
    Write-Output "Virtual environment not found. Creating Virtual Environment: $venv"

    python -m venv $venv
} else {
    Write-Output "Virtual environment already exists. Skipping creation."
}


# Call the activation script
Write-Output "Running Virtual Environment: $activatePath"
& $activatePath

# Install requirements
Write-Output "Installing requirements"
& python -m pip install -r $requirements

# Run python
Write-Output "Running Script $source"

& python $pyFlags $source

