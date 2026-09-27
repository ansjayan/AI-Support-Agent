# Test 5 — Loyalty Calculation via Deployed AgentCore Runtime

## Purpose

Verify that the deployed AgentCore agent performs the Gold loyalty calculation using Code Interpreter and returns deterministic calculation results.

## Invocation

```powershell

agentcore --% invoke -s loyalty-calculation-0000000000005 {"prompt":"I am a Gold loyalty member with 4250 points and I have a $150 standard order. Calculate the best loyalty discount, including points redeemed, points discount, Gold tier discount, total savings, final total, points earned, and remaining points."}



@'
{
  "prompt": "I am a Gold loyalty member with 4250 points. My order total is 150 dollars and the product category is standard. Calculate my loyalty discount, final total, points redeemed, points earned, and remaining points.",
  "customer_id": "CUST-FINAL-LOYALTY",
  "session_id": "final-loyalty-session-001"
}
'@ | Set-Content -Encoding utf8 .\payload-final-test5.json
Remove-Item .\output-final-test5.json -ErrorAction SilentlyContinue
aws bedrock-agentcore invoke-agent-runtime `
  --agent-runtime-arn "arn:aws:bedrock-agentcore:us-east-1:085621837147:runtime/customer_support_agent-jUA02g6Mfc" `
  --qualifier "DEFAULT" `
  --runtime-session-id "final-loyalty-runtime-session-000000002" `
  --content-type "application/json" `
  --accept "application/json" `
  --payload fileb://payload-final-test5.json `
  --region us-east-1 `
  --cli-binary-format raw-in-base64-out `
  --no-cli-pager `
  .\output-final-test5.json
Write-Host "`n=== FINAL TEST 5 — LOYALTY CALCULATION ==="
Get-Content .\output-final-test5.json -Raw