# CareConnect API Demo Script
# ============================
# This PowerShell script demonstrates the CareConnect AI agent
# by making HTTP calls to the API endpoints.
#
# Prerequisites:
#   1. Docker containers running: docker-compose up -d
#   2. Database seeded: docker-compose exec backend python scripts/seed_demo_data.py
#
# Usage:
#   .\demo_api_test.ps1
#   .\demo_api_test.ps1 -Quick
#   .\demo_api_test.ps1 -Interactive

param(
    [switch]$Quick,
    [switch]$Interactive
)

# Configuration
$BaseUrl = "http://localhost:8000/api/v1"
$SessionId = "demo-session-" + (Get-Date -Format "yyyyMMddHHmmss")

# Colors for output
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan -NoNewline
    Write-Host "" -ForegroundColor White
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Scene {
    param([string]$Act, [string]$Scene, [string]$Title)
    Write-Host ""
    Write-Host "--- $Act, $Scene : $Title ---" -ForegroundColor Yellow
    Write-Host ""
}

function Write-User {
    param([string]$Message)
    Write-Host "👤 User: " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Agent {
    param([string]$Message)
    Write-Host "🤖 Agent: " -ForegroundColor Blue -NoNewline
    Write-Host $Message
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "   ℹ️  $Message" -ForegroundColor DarkGray
}

# Function to send a message to the agent
function Send-AgentMessage {
    param(
        [string]$Message,
        [string]$Session = $SessionId
    )
    
    try {
        $body = @{
            message = $Message
            session_id = $Session
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/agent/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
        
        return $response.response
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Demo scenarios
function Run-FullDemo {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                                                                    ║" -ForegroundColor Magenta
    Write-Host "║     🏥 CARECONNECT AI AGENT - API DEMO 🤖                         ║" -ForegroundColor Magenta
    Write-Host "║                                                                    ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Session ID: $SessionId" -ForegroundColor DarkGray
    Write-Host ""
    
    # Act 1: Information Queries
    Write-Header "ACT 1: INFORMATION QUERIES (RAG)"
    
    Write-Scene "Act 1" "Scene 1" "Greeting"
    Write-User "Hi! What can you help me with?"
    $response = Send-AgentMessage "Hi! What can you help me with?"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    Write-Scene "Act 1" "Scene 2" "Parking Information"
    Write-User "Where can I park at the hospital?"
    $response = Send-AgentMessage "Where can I park at the hospital?" -Session "$SessionId-parking"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    Write-Scene "Act 1" "Scene 3" "Lab Hours"
    Write-User "What are the laboratory hours?"
    $response = Send-AgentMessage "What are the laboratory hours?" -Session "$SessionId-hours"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    # Act 2: Finding Doctors
    Write-Header "ACT 2: FINDING DOCTORS"
    
    Write-Scene "Act 2" "Scene 1" "List Cardiology Doctors"
    Write-User "Who are the doctors in the Cardiology department?"
    $response = Send-AgentMessage "Who are the doctors in the Cardiology department?" -Session "$SessionId-doctors"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    # Act 3: Booking
    Write-Header "ACT 3: BOOKING APPOINTMENTS"
    
    $bookingSession = "$SessionId-booking"
    
    Write-Scene "Act 3" "Scene 1" "Request Appointment"
    Write-User "I need to book an appointment with a cardiologist tomorrow"
    $response = Send-AgentMessage "I need to book an appointment with a cardiologist tomorrow" -Session $bookingSession
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    Write-Scene "Act 3" "Scene 2" "Select Time"
    Write-User "The 10:00 AM slot works for me"
    $response = Send-AgentMessage "The 10:00 AM slot works for me" -Session $bookingSession
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    # Act 4: View Appointments
    Write-Header "ACT 4: VIEW APPOINTMENTS"
    
    Write-Scene "Act 4" "Scene 1" "View Upcoming"
    Write-User "Show me my upcoming appointments"
    $response = Send-AgentMessage "Show me my upcoming appointments" -Session "$SessionId-view"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    # Act 5: Safety Boundaries
    Write-Header "ACT 5: SAFETY BOUNDARIES"
    
    Write-Scene "Act 5" "Scene 1" "Emergency Detection"
    Write-Info "Agent should immediately direct to 911"
    Write-User "I have severe chest pain and difficulty breathing"
    $response = Send-AgentMessage "I have severe chest pain and difficulty breathing" -Session "$SessionId-emergency"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    Write-Scene "Act 5" "Scene 2" "Medical Advice Rejection"
    Write-Info "Agent should refuse medical advice"
    Write-User "What medicine should I take for my headache?"
    $response = Send-AgentMessage "What medicine should I take for my headache?" -Session "$SessionId-advice"
    if ($response) { Write-Agent $response }
    Start-Sleep -Seconds 2
    
    # Finale
    Write-Header "DEMO COMPLETE! 🎉"
    Write-Host ""
    Write-Host "The CareConnect AI Agent demonstrated:" -ForegroundColor Green
    Write-Host "  ✅ Facility information via RAG" -ForegroundColor White
    Write-Host "  ✅ Doctor/provider search" -ForegroundColor White
    Write-Host "  ✅ Appointment booking" -ForegroundColor White
    Write-Host "  ✅ Viewing appointments" -ForegroundColor White
    Write-Host "  ✅ Emergency detection" -ForegroundColor White
    Write-Host "  ✅ Medical advice boundaries" -ForegroundColor White
    Write-Host ""
}

function Run-QuickDemo {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║     🏥 CARECONNECT - QUICK DEMO                                   ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    $scenarios = @(
        @{ Title = "1/4: Information Query"; Message = "Where can I park at the hospital?" },
        @{ Title = "2/4: Find Doctors"; Message = "Who are the doctors in Dermatology?" },
        @{ Title = "3/4: Book Appointment"; Message = "Book me an appointment with a dermatologist tomorrow at 10 AM" },
        @{ Title = "4/4: Emergency Detection"; Message = "I have severe chest pain" }
    )
    
    foreach ($scenario in $scenarios) {
        Write-Host "--- $($scenario.Title) ---" -ForegroundColor Yellow
        Write-User $scenario.Message
        $response = Send-AgentMessage $scenario.Message -Session "$SessionId-$($scenario.Title)"
        if ($response) { Write-Agent $response }
        Start-Sleep -Seconds 1
    }
    
    Write-Host "✅ Quick demo complete!" -ForegroundColor Green
    Write-Host ""
}

function Run-InteractiveMode {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║     🏥 CARECONNECT - INTERACTIVE MODE                             ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Type your messages to chat with the agent." -ForegroundColor Cyan
    Write-Host "Commands: 'quit' to exit, 'new' for new session" -ForegroundColor DarkGray
    Write-Host ""
    
    $session = $SessionId
    
    while ($true) {
        $userInput = Read-Host "You"
        
        if ([string]::IsNullOrWhiteSpace($userInput)) {
            continue
        }
        
        if ($userInput.ToLower() -eq 'quit') {
            Write-Host "Goodbye!" -ForegroundColor Cyan
            break
        }
        
        if ($userInput.ToLower() -eq 'new') {
            $session = "demo-session-" + (Get-Date -Format "yyyyMMddHHmmss")
            Write-Host "New session started: $session" -ForegroundColor DarkGray
            continue
        }
        
        $response = Send-AgentMessage $userInput -Session $session
        if ($response) {
            Write-Host "Agent: $response" -ForegroundColor Blue
            Write-Host ""
        }
    }
}

# Main execution
if ($Interactive) {
    Run-InteractiveMode
} elseif ($Quick) {
    Run-QuickDemo
} else {
    Run-FullDemo
}
