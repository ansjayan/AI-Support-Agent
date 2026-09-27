## Project Reflection

This project gave me practical experience building and deploying a production-style customer support AI agent using Amazon Bedrock AgentCore and the Strands Agents SDK. The final solution integrates multiple AgentCore capabilities rather than relying only on a language model. AgentCore Gateway connects the agent to an order-tracking REST API and a refund-processing Lambda function, while AgentCore Memory provides long-term semantic and user-preference memory across sessions. The Knowledge Base enables retrieval of customer-support and loyalty information, Code Interpreter performs deterministic loyalty calculations, and the Browser tool allows the agent to retrieve information from web pages.

One of the most important lessons was understanding how these components work together. The language model handles reasoning and conversation, while specialized tools perform actions or calculations and provide grounded information. For example, the loyalty calculation initially demonstrated that correct tool output can still be incorrectly interpreted by the model. I addressed this by capturing the authoritative Code Interpreter result with a Strands `AfterToolCallEvent` hook and returning the deterministic values while maintaining a customer-friendly response.

Another challenge was working within the restricted IAM permissions of the provided AWS lab environment. Some CLI operations were explicitly denied, so I used the AWS Management Console for affected deployment and configuration tasks without changing the intended architecture.

Finally, I added CloudWatch monitoring with an `ERROR` metric filter and an alarm for more than five errors within five minutes. I validated the deployed system with six end-to-end tests covering order tracking, refunds, Knowledge Base retrieval, cross-session memory, loyalty calculations, and browser access. This project helped me understand how AgentCore can combine LLM reasoning, persistent memory, enterprise data, external tools, deterministic computation, deployment, and observability into a single production-oriented AI agent.


