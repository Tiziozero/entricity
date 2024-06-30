# MyFirstScript.ps1
$source = ".\src\main.py"
$venv = "evenv"

# Using string interpolation to include the variable in the path
$activatePath = ".\$venv\Scripts\activate"

Write-Output "Running Virtual Environment: $activatePath"

# Call the activation script
& $activatePath


Write-Output "Running Script $source"

python $source


