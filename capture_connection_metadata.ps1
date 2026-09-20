[CmdletBinding()]
param(
    [string]$ProcessName = "Dauntless-Win64-Shipping",
    [ValidateRange(1, 60)]
    [int]$IntervalSeconds = 2,
    [string]$OutputDirectory = ".\research\local-captures"
)

$ErrorActionPreference = "Stop"
$outputPath = [System.IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = Join-Path $outputPath "connection-metadata-$stamp.csv"
$dnsPath = Join-Path $outputPath "dns-metadata-$stamp.csv"

"timestamp_utc,process_id,protocol,local_address,local_port,remote_address,remote_port,state" |
    Set-Content -LiteralPath $csvPath -Encoding utf8
"timestamp_utc,dns_name,record_type,address" |
    Set-Content -LiteralPath $dnsPath -Encoding utf8

Write-Host "Waiting for process '$ProcessName'. Start it normally when ready."
Write-Host "Only socket metadata is recorded; packet payloads and credentials are not captured."
Write-Host "Press Ctrl+C after login, matchmaking, and travel have completed."
Write-Host "Output: $csvPath"
Write-Host "DNS output: $dnsPath"

$seenProcess = $false
try {
    while ($true) {
        $processes = @(Get-Process -Name $ProcessName -ErrorAction SilentlyContinue)
        if ($processes.Count -gt 0) {
            $seenProcess = $true
            $timestamp = (Get-Date).ToUniversalTime().ToString("o")
            Get-DnsClientCache -ErrorAction SilentlyContinue |
                Where-Object { $_.Data -and $_.Type -in 1, 28 } |
                ForEach-Object {
                    [pscustomobject]@{
                        timestamp_utc = $timestamp
                        dns_name = $_.Entry
                        record_type = if ($_.Type -eq 28) { "AAAA" } else { "A" }
                        address = $_.Data
                    }
                } | Export-Csv -LiteralPath $dnsPath -Append -NoTypeInformation
            foreach ($process in $processes) {
                $connections = @(Get-NetTCPConnection -OwningProcess $process.Id -ErrorAction SilentlyContinue)
                foreach ($connection in $connections) {
                    [pscustomobject]@{
                        timestamp_utc = $timestamp
                        process_id = $process.Id
                        protocol = "TCP"
                        local_address = $connection.LocalAddress
                        local_port = $connection.LocalPort
                        remote_address = $connection.RemoteAddress
                        remote_port = $connection.RemotePort
                        state = $connection.State
                    } | Export-Csv -LiteralPath $csvPath -Append -NoTypeInformation
                }

                $listeners = @(Get-NetUDPEndpoint -OwningProcess $process.Id -ErrorAction SilentlyContinue)
                foreach ($listener in $listeners) {
                    [pscustomobject]@{
                        timestamp_utc = $timestamp
                        process_id = $process.Id
                        protocol = "UDP-local"
                        local_address = $listener.LocalAddress
                        local_port = $listener.LocalPort
                        remote_address = ""
                        remote_port = ""
                        state = "Bound"
                    } | Export-Csv -LiteralPath $csvPath -Append -NoTypeInformation
                }
            }
        } elseif ($seenProcess) {
            Write-Host "The process exited; capture stopped."
            break
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
} finally {
    Write-Host "Saved metadata to $csvPath"
    Write-Host "Saved DNS metadata to $dnsPath"
}
