@'
{
  "prompt": "My name is Jane and I prefer concise responses. Please remember this preference.",
  "customer_id": "CUST-FINAL-MEMORY-JANE",
  "session_id": "final-memory-session-A"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test4a.json

Remove-Item .\output-final-test4a.json -ErrorAction SilentlyContinue

aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-memory-runtime-session-A-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test4a.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test4a.json

Get-Content .\output-final-test4a.json -Raw



@'
{
  "prompt": "What is my name and how do I prefer you to respond?",
  "customer_id": "CUST-FINAL-MEMORY-JANE",
  "session_id": "final-memory-session-B"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test4b.json

Remove-Item .\output-final-test4b.json -ErrorAction SilentlyContinue

aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-memory-runtime-session-B-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test4b.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test4b.json

Write-Host "`n=== FINAL TEST 4B — CROSS-SESSION MEMORY ==="
Get-Content .\output-final-test4b.json -Raw



