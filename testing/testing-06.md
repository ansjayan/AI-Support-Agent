# Test 6 — Browser Tool via Deployed AgentCore Runtime

## Purpose

Verify that the deployed AgentCore agent can use the Browser tool to access a public web page and retrieve its page title.

## Invocation

```powershell

agentcore --% invoke -s browser-tool-00000000000000000006- {"prompt":"Use the browser tool to visit https://www.amazon.com and tell me the page title."}



@'
{
  "prompt": "Use the browser tool to visit https://www.amazon.com and tell me the page title.",
  "customer_id": "CUST-FINAL-BROWSER",
  "session_id": "final-browser-session-001"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test6.json
Remove-Item .\output-final-test6.json -ErrorAction SilentlyContinue
aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-browser-runtime-session-000000001" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test6.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --cli-read-timeout 600 `
  --no-cli-pager `
  .\output-final-test6.json
Write-Host "`n=== FINAL TEST 6 — BROWSER ==="
Get-Content .\output-final-test6.json -Raw