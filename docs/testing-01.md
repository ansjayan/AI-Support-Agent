@'
{
  "prompt": "Where is my order ORD-001?",
  "customer_id": "CUST-FINAL-ORDER",
  "session_id": "final-order-session-001"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test1.json
Remove-Item .\output-final-test1.json -ErrorAction SilentlyContinue
aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-order-runtime-session-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test1.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test1.json
Write-Host "`n=== FINAL TEST 1 — ORDER TRACKING ==="
Get-Item .\output-final-test1.json | Select-Object Name, LastWriteTime, Length
Get-Content .\output-final-test1.json -Raw