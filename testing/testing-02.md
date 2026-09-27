@'
{
  "prompt": "I want a refund for order ORD-002. The Kindle Paperwhite arrived damaged.",
  "customer_id": "CUST-FINAL-REFUND",
  "session_id": "final-refund-session-001"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test2.json
Remove-Item .\output-final-test2.json -ErrorAction SilentlyContinue
aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-refund-runtime-session-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test2.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test2.json
Write-Host "`n=== FINAL TEST 2 — REFUND ==="
Get-Item .\output-final-test2.json | Select-Object Name, LastWriteTime, Length
Get-Content .\output-final-test2.json -Raw