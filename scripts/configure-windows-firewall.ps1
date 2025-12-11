# Configure Windows Firewall for ABParts Mobile Access
# This script adds firewall rules to allow mobile device access to ABParts services
# Run this script as Administrator

param(
    [switch]$Remove,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Show-Help {
    Write-Host "ABParts Windows Firewall Configuration Script" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\configure-windows-firewall.ps1          # Add firewall rules"
    Write-Host "  .\configure-windows-firewall.ps1 -Remove  # Remove firewall rules"
    Write-Host "  .\configure-windows-firewall.ps1 -Help    # Show this help"
    Write-Host ""
    Write-Host "This script must be run as Administrator to modify firewall rules."
    Write-Host ""
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Add-FirewallRules {
    Write-Info "Adding Windows Firewall rules for ABParts mobile access..."
    
    $rules = @(
        @{Name="ABParts Frontend"; Port=3000; Description="Allow access to ABParts React frontend"},
        @{Name="ABParts API"; Port=8000; Description="Allow access to ABParts FastAPI backend"},
        @{Name="ABParts Admin"; Port=8080; Description="Allow access to ABParts pgAdmin interface"}
    )
    
    $success = 0
    $total = $rules.Count
    
    foreach ($rule in $rules) {
        try {
            # Check if rule already exists
            $existingRule = Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
            if ($existingRule) {
                Write-Warning "Firewall rule '$($rule.Name)' already exists, updating..."
                Remove-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
            }
            
            # Add the new rule
            New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Protocol TCP -LocalPort $rule.Port -Action Allow -Description $rule.Description | Out-Null
            Write-Success "Added firewall rule: $($rule.Name) (Port $($rule.Port))"
            $success++
        }
        catch {
            Write-Error "Failed to add firewall rule: $($rule.Name) - $($_.Exception.Message)"
        }
    }
    
    Write-Info "Firewall configuration complete: $success/$total rules added successfully"
    
    if ($success -eq $total) {
        Write-Success "All firewall rules added successfully!"
        Write-Info "Your mobile devices should now be able to access ABParts services."
        Write-Info ""
        Write-Info "Test mobile access at:"
        
        # Try to get HOST_IP from .env.local
        $envFile = ".\.env.local"
        if (Test-Path $envFile) {
            $hostIP = (Get-Content $envFile | Where-Object { $_ -match "^HOST_IP=" } | ForEach-Object { $_.Split("=")[1] }) | Select-Object -First 1
            if ($hostIP) {
                Write-Info "  📱 Frontend: http://$hostIP:3000"
                Write-Info "  🔧 API: http://$hostIP:8000"
                Write-Info "  📚 API Docs: http://$hostIP:8000/docs"
                Write-Info "  🗄️ Admin: http://$hostIP:8080"
            }
        }
    }
}

function Remove-FirewallRules {
    Write-Info "Removing Windows Firewall rules for ABParts..."
    
    $ruleNames = @("ABParts Frontend", "ABParts API", "ABParts Admin")
    $removed = 0
    
    foreach ($ruleName in $ruleNames) {
        try {
            $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
            if ($existingRule) {
                Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
                Write-Success "Removed firewall rule: $ruleName"
                $removed++
            } else {
                Write-Warning "Firewall rule not found: $ruleName"
            }
        }
        catch {
            Write-Error "Failed to remove firewall rule: $ruleName - $($_.Exception.Message)"
        }
    }
    
    Write-Info "Firewall cleanup complete: $removed rules removed"
}

function Show-CurrentRules {
    Write-Info "Current ABParts firewall rules:"
    
    $ruleNames = @("ABParts Frontend", "ABParts API", "ABParts Admin")
    $found = 0
    
    foreach ($ruleName in $ruleNames) {
        $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        if ($rule) {
            $portFilter = $rule | Get-NetFirewallPortFilter
            Write-Success "$ruleName - Port $($portFilter.LocalPort) - $($rule.Action)"
            $found++
        }
    }
    
    if ($found -eq 0) {
        Write-Warning "No ABParts firewall rules found"
    } else {
        Write-Info "Found $found ABParts firewall rules"
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Info "=== ABParts Windows Firewall Configuration ==="
Write-Host ""

# Check if running as Administrator
if (-not (Test-Administrator)) {
    Write-Error "This script must be run as Administrator to modify firewall rules."
    Write-Info "Please right-click PowerShell and select 'Run as Administrator', then run this script again."
    Write-Host ""
    Write-Info "Alternative: Run these commands manually in an Administrator Command Prompt:"
    Write-Host "netsh advfirewall firewall add rule name=`"ABParts Frontend`" dir=in action=allow protocol=TCP localport=3000"
    Write-Host "netsh advfirewall firewall add rule name=`"ABParts API`" dir=in action=allow protocol=TCP localport=8000"
    Write-Host "netsh advfirewall firewall add rule name=`"ABParts Admin`" dir=in action=allow protocol=TCP localport=8080"
    exit 1
}

# Show current rules first
Show-CurrentRules
Write-Host ""

if ($Remove) {
    Remove-FirewallRules
} else {
    Add-FirewallRules
}

Write-Host ""
Write-Success "Firewall configuration complete!"
Write-Info "You can now test mobile access to your ABParts application."