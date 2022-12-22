# Returns JSON as object
$json = Get-Content -Raw -LiteralPath ".\my_data.json" -Encoding UTF8 | ConvertFrom-Json
# Display value
$json.Programs[0].Name
