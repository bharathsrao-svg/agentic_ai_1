# PowerShell script to test MCP get_holdings
# Run with: .\test_mcp_powershell.ps1

$mcpUrl = "http://localhost:8000/mcp"

# Create request body
$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "tools/call"
    params = @{
        name = "get_holdings"
        arguments = @{}
    }
} | ConvertTo-Json -Depth 10

Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host "MCP REQUEST FOR get_holdings (PowerShell)"
Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host ""
Write-Host "URL: $mcpUrl"
Write-Host ""
Write-Host "Method: POST"
Write-Host ""
Write-Host "Request Body:"
Write-Host $body
Write-Host ""
Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host "SENDING REQUEST"
Write-Host "=" -NoNewline
Write-Host ("=" * 79)
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $mcpUrl `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host ""
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "Response:"
    Write-Host ($result | ConvertTo-Json -Depth 10)
    Write-Host ""
    
    if ($result.result -and $result.result.content) {
        $holdings = $result.result.content
        Write-Host "[SUCCESS] Got $($holdings.Count) holdings!"
        foreach ($h in $holdings[0..2]) {
            Write-Host "  - $($h.tradingsymbol): $($h.quantity) units"
        }
    }
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Make sure the MCP server is running:"
    Write-Host "  python simple_mcp_server_example.py"
}

