@'
{
  "prompt": "What benefits do Platinum loyalty members receive?",
  "customer_id": "CUST-FINAL-KB",
  "session_id": "final-kb-session-001"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test3.json
Remove-Item .\output-final-test3.json -ErrorAction SilentlyContinue
aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-kb-runtime-session-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test3.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test3.json
Write-Host "`n=== FINAL TEST 3 — KNOWLEDGE BASE ==="
Get-Item .\output-final-test3.json | Select-Object Name, LastWriteTime, Length
Get-Content .\output-final-test3.json -Raw