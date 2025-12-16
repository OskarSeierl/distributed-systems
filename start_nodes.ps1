# Define the parameter at the start of the script
# $NodeCount defaults to 5 if no argument is given
param (
    [int]$NodeCount = 5
)

Write-Host "Starting Blockchain Simulation with $NodeCount nodes..." -ForegroundColor Green

# Loop from 0 to (NodeCount - 1)
0..($NodeCount - 1) | ForEach-Object {
    $nodeId = $_
    $port = 8000 + $nodeId

    # Construct the command string
    $args = "python -m src.noobcash.api --port $port --ip 127.0.0.1"

    if ($nodeId -eq 0) {
        Write-Host "Starting Bootstrap Node 0 on port $port" -ForegroundColor Cyan
        # Open a new CMD window running the python command
        Start-Process cmd -ArgumentList "/k $args"
    }
    else {
        Write-Host "Starting Node $nodeId on port $port" -ForegroundColor Yellow
        Start-Process cmd -ArgumentList "/k $args"
    }

    # Wait for the previous node to initialize
    Start-Sleep -Seconds 5
}

Write-Host "All nodes launched!" -ForegroundColor Green