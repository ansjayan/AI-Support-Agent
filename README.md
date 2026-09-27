# AI Support Agent

An intelligent, cloud-deployed customer support agent built using **Amazon Bedrock AgentCore** and the **Strands Agents SDK**.

This project demonstrates how to build an AI agent that goes beyond a traditional chatbot by combining a foundation model with external tools, Retrieval-Augmented Generation (RAG), persistent memory, secure code execution, and live web browsing.

The agent acts as a conversational interface between customers and a fictional e-commerce platform. Through a single conversation, customers can track orders, process refunds, ask questions about products and policies, calculate loyalty rewards, and retrieve information from live web pages.

## What the Agent Can Do

The AI Support Agent supports six core capabilities:

### 1. Order Tracking

The agent can retrieve order and customer information through **Amazon Bedrock AgentCore Gateway**.

Order data is exposed through an API Gateway REST API backed by an AWS Lambda function. The Gateway makes these operations available to the AI agent as tools using the **Model Context Protocol (MCP)**.

Example:

> "Can you track order ORD-001?"

The agent can return information such as the order status, carrier, tracking number, and estimated delivery date.

### 2. Refund Processing

Customers can request refunds conversationally.

A refund-processing AWS Lambda function is exposed as another AgentCore Gateway target. The agent can select and invoke the appropriate refund tool based on the customer's request.

Example:

> "I want to return my Kindle Paperwhite from order ORD-002. Please initiate a refund."

The tool can return a refund ID, approval status, refund amount, and estimated processing time.

### 3. Retrieval-Augmented Generation (RAG)

The agent uses an **Amazon Bedrock Knowledge Base** to answer questions using grounded information from the project's product catalog and customer-support documentation.

The knowledge base contains information about:

* Products and specifications
* Return and refund policies
* Warranty information
* Loyalty rewards
* Order-status definitions

Instead of relying only on the language model's existing knowledge, the agent retrieves relevant information from the knowledge base before answering.

### 4. Cross-Session Customer Memory

The project uses **Amazon Bedrock AgentCore Memory** to maintain customer information across separate conversations.

The agent can remember information such as a customer's name and communication preferences even when the customer starts a new session.

For example, a customer might say:

> "Hi, I am Jane. I prefer concise responses."

In a later session using the same customer ID, the agent can retrieve this information and personalize its response.

This demonstrates the difference between temporary conversation history and persistent, customer-specific long-term memory.

### 5. Loyalty Discount Calculation

The agent uses **AgentCore Code Interpreter** to perform exact loyalty reward and discount calculations inside a secure sandbox.

The calculation considers:

* Current loyalty points
* Customer membership tier
* Order total
* Product category
* Redeemed points
* Tier discount
* Newly earned points
* Remaining loyalty points

This allows deterministic calculations to be handled by executable code rather than relying on the language model to perform arithmetic itself.

### 6. Live Web Browsing

The agent integrates the **AgentCore Browser Tool**, allowing it to access live web pages when current external information is required.

This extends the agent beyond static training data and the project's internal knowledge base.

## Architecture

The project combines several AWS and AI-agent technologies:

```text
Customer
   │
   ▼
Amazon Bedrock AgentCore Runtime
   │
   ▼
Strands AI Agent
   │
   ├── AgentCore Gateway / MCP
   │      ├── API Gateway → Order Tracking Lambda
   │      └── Refund Processing Lambda
   │
   ├── Bedrock Knowledge Base
   │      └── Product & Support Documentation
   │
   ├── AgentCore Memory
   │      └── Cross-session customer context
   │
   ├── AgentCore Code Interpreter
   │      └── Loyalty calculations
   │
   └── AgentCore Browser
          └── Live web access
```

The agent itself is implemented with the **Strands Agents SDK** and deployed to **Amazon Bedrock AgentCore Runtime**.

## Technologies Used

* Python
* Amazon Bedrock
* Amazon Bedrock AgentCore Runtime
* Amazon Bedrock AgentCore Gateway
* Amazon Bedrock AgentCore Memory
* Amazon Bedrock Knowledge Bases
* Amazon Bedrock AgentCore Code Interpreter
* Amazon Bedrock AgentCore Browser
* Strands Agents SDK
* Model Context Protocol (MCP)
* AWS Lambda
* Amazon API Gateway
* Amazon S3
* Amazon OpenSearch Serverless
* Amazon CloudWatch
* AWS IAM
* `boto3`
* `uv`
* Git and GitHub

## Project Goal

The goal of this project is to demonstrate how multiple AI-agent capabilities can be combined into a single production-style conversational application.

Rather than implementing customer support as one large prompt, individual responsibilities are delegated to specialized services and tools. The language model determines what the customer needs, while AgentCore and AWS services provide controlled access to external APIs, persistent memory, enterprise knowledge, computation, and the web.

The result is an AI support agent capable of handling multi-step customer requests while maintaining context and grounding its responses in external systems.
