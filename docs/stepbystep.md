


Yes. I understand what you want now.

From this point onward, I won't treat you as someone merely following AWS commands. I'll treat this as **building the project together while teaching you how to think like the engineer building it**.

For every new piece, we'll discuss four things before executing it: **What are we trying to accomplish? Why do we need it? How should we design it? What exactly are we going to execute?** Then you'll run it, show me the result, and we'll interpret what happened together.

But because we've already built quite a bit without doing that properly, we should first reconstruct the project from zero in very simple terms.

# Start with the simplest possible idea

Forget AWS, MCP, Lambda, Strands, Bedrock and all those names for a moment.

Imagine you own an online shop.

A customer opens a chat and says:

> Where is my order ORD-001?

A normal ChatGPT-like model doesn't know your private order database.

So we need to give our AI a way to **do things**.

Conceptually:

```text
Customer
   │
   │ "Where is ORD-001?"
   ▼
   AI
   │
   │ "I need order information."
   ▼
   Order System
   │
   │ ORD-001 is shipped via UPS
   ▼
   AI
   │
   ▼
Customer receives answer
```

That's the heart of this entire project.

Everything else we're building exists to make that process work safely and reliably.

---

# What kind of AI are we building?

We're building a **customer-support AI agent**.

There is an important distinction between an ordinary LLM and an agent.

An LLM can receive text and generate text:

```text
Question
   ↓
LLM
   ↓
Answer
```

An **agent** can reason about a request and choose tools:

```text
Question
   ↓
Agent
   │
   ├── maybe call Order tool
   ├── maybe call Refund tool
   ├── maybe search company documents
   ├── maybe remember customer preferences
   ├── maybe calculate something
   └── maybe browse a website
   ↓
Answer
```

That's what this assignment is teaching you.

---

# Meet our imaginary customer Jane

We'll use Jane throughout our learning.

Jane says:

> Where is order ORD-001?

Our agent should recognize:

> This requires order information.

So it calls an order-tracking tool.

Jane later says:

> Refund my Kindle from ORD-002.

The agent recognizes:

> That's a refund operation.

It calls the refund tool.

Then Jane asks:

> What benefits do Platinum customers receive?

That's not an order lookup. The answer exists in our company documentation.

So the agent searches the Knowledge Base.

Later Jane says:

> I prefer concise answers.

Tomorrow she starts a new chat.

She asks:

> Do you remember my preference?

Our agent retrieves that information from Memory.

Then:

> I'm Gold, have 4,250 points and my order is $150. What's my discount?

The agent can use Code Interpreter to perform the calculation.

Finally:

> Check something on Amazon's website.

It can use Browser.

Those are essentially the six capabilities we're building. Your project instructions define corresponding final tests for order tracking, refund processing, RAG, memory, loyalty calculations and browser use. 

---

# So where does the AI itself live?

Eventually, here:

```text
main.py
```

Think of `main.py` as the **brain assembly room**.

We're going to create something roughly like:

```text
main.py
│
├── AI model
│
├── instructions
│
├── order tools
│
├── refund tools
│
├── knowledge search
│
├── memory
│
├── calculator
│
└── browser
```

But we deliberately did **not** start by completing `main.py`.

Why?

Because if we connected seven unfinished systems simultaneously and something broke, you wouldn't know which system caused the failure.

Instead we're following a professional engineering idea:

> Build small pieces → test each piece → connect them → test the connections.

---

# Think of building a car

Suppose we're making a car.

It would be a bad idea to manufacture everything, assemble the whole vehicle and only then ask:

> Does the engine work?

Instead:

```text
Build engine
→ test engine

Build transmission
→ test transmission

Build brakes
→ test brakes

Connect them
→ test integration

Build entire car
→ road test
```

We're doing exactly that with your AI system.

---

# Our complete architecture

Eventually the system will look approximately like this:

```text
                         CUSTOMER
                            │
                            ▼
                    AgentCore Runtime
                            │
                            ▼
                       main.py
                            │
                            ▼
                     STRANDS AGENT
                            │
       ┌────────────────────┼──────────────────┐
       │                    │                  │
       ▼                    ▼                  ▼
      MCP               Knowledge           Memory
       │                   Base                │
       ▼                    │                  │
AgentCore Gateway           │                  │
       │                    │                  │
  ┌────┴────┐               │                  │
  │         │               │                  │
Order     Refund            │                  │
Tool      Tool              │                  │
  │         │               │                  │
  ▼         ▼               ▼                  ▼
API      Lambda          Documents        Customer facts
Gateway                                  /preferences
  │
  ▼
Lambda


Strands Agent
     │
     ├── Code Interpreter
     │
     └── Browser
```

Don't try to memorize that yet.

By the time we've built everything, that diagram should feel obvious.

---

# First concept: what is AWS?

Before understanding Lambda or API Gateway, understand AWS itself.

Imagine you need another computer.

Traditionally you buy:

```text
Computer
CPU
RAM
Hard disk
Network
```

put it somewhere and run your software.

AWS lets you rent computing services over the internet.

Instead of buying servers, you can say:

> AWS, run this Python function when someone needs it.

That's essentially where Lambda enters the story.

---

# What is Lambda?

Consider this tiny Python function:

```python
def add(a, b):
    return a + b
```

If it runs on your laptop, your laptop must be running.

But suppose we put the function in AWS.

Then AWS can run it for us.

That's the basic idea of:

**AWS Lambda.**

It's a way to run code without us managing a traditional server continuously.

---

# Why do we have two Lambdas?

Our starter project supplied:

```text
order_tracker.py
refund_processor.py
```

These solve different jobs.

Think:

```text
Employee #1
Order Department
→ order_tracker.py

Employee #2
Refund Department
→ refund_processor.py
```

We deployed them separately as:

```text
order-tracker
refund-processor
```

Now AWS knows how to execute both jobs.

---

# Let's actually understand `order_tracker.py`

The important part is conceptually:

```python
def lambda_handler(event, context):
```

AWS Lambda needs an entry point.

When something calls the Lambda, AWS essentially says:

> Here's the incoming request.

That request arrives as:

```python
event
```

So imagine:

```text
Someone asks something
       ↓
AWS Lambda
       ↓
lambda_handler(event, context)
                    ↑
          information about request
```

Your supplied function examines things such as the HTTP method, API resource template and path parameters to decide whether the caller wants an individual order, a customer's details or a customer's orders. 

---

# What is ORD-001?

For this assignment we're not connecting a real Amazon order database.

The starter file contains sample data.

Conceptually:

```python
ORDERS = {
    "ORD-001": {
        "customer_id": "CUST-123",
        "status": "SHIPPED",
        ...
    }
}
```

Therefore when we ask:

```text
ORD-001
```

the function searches the sample data.

It returns information including:

```text
SHIPPED
UPS
TRK987654321
```

That's why we saw those values during our test. The supplied data defines `ORD-001` as Jane's shipped Wireless Headphones Pro order. 

---

# Why did we test Lambda directly?

This is an important engineering lesson.

Before adding API Gateway, we asked:

> Does `order-tracker` itself work?

We gave it a simulated request.

It returned the correct order.

Therefore we established:

```text
order-tracker
     ↓
    WORKS
```

That's useful because if API Gateway fails later, we know:

> The underlying Lambda was already working.

We have narrowed the possible problem.

---

# Now API Gateway

This is probably one of the parts that currently feels mysterious.

Imagine the `order-tracker` Lambda is an employee sitting inside a locked office.

Customers cannot simply walk into the office.

We put a reception desk outside.

That receptionist is:

**API Gateway.**

```text
Customer
    │
    ▼
Reception desk
(API Gateway)
    │
    ▼
Order employee
(Lambda)
```

API Gateway receives HTTP requests and routes them to the appropriate backend.

---

# What's HTTP?

You've used HTTP your whole life.

When a browser communicates with a website, it can make requests such as:

```text
GET /something
```

`GET` essentially means:

> Give me information.

Our application supports:

```text
GET /orders/ORD-001
```

which conceptually means:

> Give me information about ORD-001.

---

# Why didn't we literally create `/orders/ORD-001`?

Because then we'd need another route for every order:

```text
/orders/ORD-001
/orders/ORD-002
/orders/ORD-003
/orders/ORD-004
...
```

Instead we created:

```text
/orders/{order_id}
```

`{order_id}` means:

> Whatever value appears here is the order ID.

Therefore:

```text
/orders/ORD-001
/orders/ORD-002
/orders/ABC-999
```

can all use the same route.

---

# You actually built that yourself

You created this hierarchy:

```text
/
└── orders
      └── {order_id}
```

Then you created:

```text
GET
```

on `{order_id}`.

Then we told API Gateway:

> When someone sends GET here, invoke `order-tracker`.

That's the `AWS_PROXY` integration we configured.

---

# What does proxy mean here?

Imagine the receptionist doesn't rewrite the customer's message.

They package the relevant request information and hand it to the employee.

So:

```text
GET /orders/ORD-001
```

becomes an event approximately like:

```json
{
    "resource": "/orders/{order_id}",
    "httpMethod": "GET",
    "pathParameters": {
        "order_id": "ORD-001"
    }
}
```

Lambda receives it.

Then the Python code can do something conceptually like:

```python
order_id = path_parameters["order_id"]
```

Now:

```text
order_id = ORD-001
```

and it can look up the order.

---

# We created two other routes too

The project also needs customer information.

So we created:

```text
/customers/{customer_id}
```

Example:

```text
/customers/CUST-123
```

Meaning:

> Tell me about customer CUST-123.

And:

```text
/customers/{customer_id}/orders
```

Example:

```text
/customers/CUST-123/orders
```

Meaning:

> Give me all orders belonging to CUST-123.

Therefore the API we just finished building structurally has:

```text
CustomerSupportOrderAPI

GET /orders/{order_id}

GET /customers/{customer_id}

GET /customers/{customer_id}/orders
```

Those match the three routes required by the supplied project instructions. 

---

# Why did we need IAM?

Now imagine our receptionist tries opening the employee's locked office.

AWS says:

> Who gave you permission?

AWS services don't automatically get unlimited access to each other.

That's where **IAM** comes in.

IAM stands for:

**Identity and Access Management.**

Think of it as AWS's security department.

It controls:

```text
WHO
can do
WHAT
to
WHICH RESOURCE
```

For example:

```text
API Gateway
can
invoke
order-tracker Lambda
```

That's why we ran `add-permission`.

---

# What was `CustomerSupportLambdaRole`?

That's another permission concept.

When Lambda itself runs, it needs an identity.

So we created:

```text
CustomerSupportLambdaRole
```

Think of it as an employee badge.

```text
order-tracker Lambda
        │
        │ wears badge
        ▼
CustomerSupportLambdaRole
```

The role currently gives Lambda the basic execution/logging permissions it needs.

This is an important AWS principle:

> Services act using identities and permissions.

You'll see IAM again when we create AgentCore components.

---

# Why is refund different?

Here's where the assignment deliberately teaches another architecture.

Orders use:

```text
Agent
 ↓
MCP
 ↓
AgentCore Gateway
 ↓
API Gateway
 ↓
order-tracker Lambda
```

Refund uses:

```text
Agent
 ↓
MCP
 ↓
AgentCore Gateway
 ↓
refund-processor Lambda
```

Notice:

```text
                Gateway
                /     \
               /       \
          REST API    Lambda
             │
             ▼
           Lambda
```

The assignment wants you to demonstrate that AgentCore Gateway can expose different kinds of backend systems as tools.

---

# Now we're getting close to MCP

This is one of the most important concepts in this project.

Imagine every tool manufacturer invented its own plug.

One laptop might need:

```text
Printer plug A
Camera plug B
Keyboard plug C
Microphone plug D
```

That's painful.

Standards solve this.

MCP — **Model Context Protocol** — gives AI applications a standardized way to interact with tools/context providers.

A useful mental model is:

> MCP is a standardized language/connection mechanism through which our AI can discover and call tools.

So instead of `main.py` containing custom hard-coded integration logic for every backend, we're going toward:

```text
Strands Agent
      │
      │ MCP
      ▼
AgentCore Gateway
      │
      ├── order tools
      └── refund tools
```

---

# What is AgentCore Gateway doing?

Think of Gateway as an **AI tool receptionist**.

Behind it are different systems:

```text
REST API
Lambda
```

But from the AI side, Gateway can expose usable tools.

The agent can discover things conceptually like:

```text
get_order
get_customer
get_customer_orders
initiate_refund
check_refund_status
get_return_label
```

The exact exposed names will depend on the Gateway target/schema configuration we create and inspect later.

The beautiful part is that the AI doesn't need to think:

> Is this REST? Lambda? Which AWS invocation format?

It interacts with tools through the Gateway/MCP layer.

---

# Then what is `MCPClient`?

Your `main.py` already imports:

```python
from strands.tools.mcp.mcp_client import MCPClient
```

Think:

```text
AgentCore Gateway = MCP side exposing tools

MCPClient = thing inside our Python application
            that connects to that MCP endpoint
```

So eventually:

```text
main.py
   │
   ▼
MCPClient
   │
   │ MCP
   ▼
AgentCore Gateway
```

Then we'll ask Gateway:

> What tools do you have?

and provide those discovered tools to the Strands agent.

Your starter also imports the streamable HTTP MCP client transport for this connection. 

---

# And MCP Inspector?

Inspector is like putting a diagnostic machine between us and MCP.

Before blaming our AI code, we can inspect/test the MCP server/Gateway.

Think:

```text
Car engine
   ↑
mechanic diagnostic tool
```

MCP Inspector plays a similar debugging role.

We can inspect available tools and manually invoke them.

That helps answer:

> Is Gateway broken?

versus:

> Is `main.py` broken?

We will use it when it adds value during the Gateway stage.

---

# What is Strands?

Eventually we need something coordinating the model and tools.

That's where the **Strands Agents SDK** enters.

Conceptually:

```python
agent = Agent(
    model=model,
    tools=tools
)
```

Then the agent receives:

> Where is ORD-001?

The model reasons:

```text
"I cannot answer from general knowledge."

"I have an order tool."

"I should call it."
```

Tool returns:

```text
SHIPPED
UPS
TRK987654321
```

Then the model constructs the natural-language response.

That's **tool use / agentic behavior**.

---

# What is Bedrock?

Amazon Bedrock provides access to foundation models and related generative-AI capabilities on AWS.

Our starter is configured around a Bedrock model, currently:

```text
global.amazon.nova-2-lite-v1:0
```

So an easy mental separation is:

```text
Bedrock model
     =
language/reasoning capability

Strands
     =
agent framework/orchestration

MCP
     =
standardized tool communication

AgentCore Gateway
     =
exposes backend capabilities as AI tools

Lambda/API Gateway
     =
actual business systems
```

That distinction is important.

---

# Then why do we need a Knowledge Base?

Suppose Jane asks:

> What's your electronics return policy?

The model shouldn't invent the company's policy.

Our actual policy is in:

```text
product_catalog.txt
```

So we need:

```text
Question
   ↓
Search our documents
   ↓
Find relevant policy
   ↓
Give information to model
   ↓
Answer
```

That's **RAG**:

**Retrieval-Augmented Generation.**

Instead of expecting the LLM to memorize our private/company information, we retrieve relevant information at query time.

Your supplied catalog, for example, states the electronics return window and loyalty benefits that the final RAG tests are designed to retrieve. 

---

# Memory solves a completely different problem

RAG:

> What does our company documentation say?

Memory:

> What do we know about this customer from previous interactions?

Jane says:

> My name is Jane. I prefer concise responses.

We store that.

Later, in another session:

> Do you remember my preference?

Memory should retrieve:

```text
Jane
prefers concise responses
```

So:

```text
Knowledge Base
      =
company knowledge

Memory
      =
customer/history knowledge
```

Don't mix those concepts.

---

# Code Interpreter solves another problem

Suppose:

```text
Customer tier = Gold
Points = 4,250
Purchase = $150
```

We don't necessarily want the language model doing arithmetic loosely in prose.

We can give it a controlled computational tool.

Conceptually:

```text
Agent
  ↓
Code Interpreter
  ↓
execute Python
  ↓
precise calculated result
```

Our `calculate_loyalty_discount` tool will eventually construct and execute the loyalty calculation and return structured values such as:

```text
points_redeemed
tier_discount_pct
final_total
remaining_points
```

That behavior is part of the supplied starter/TODO requirements. 

---

# Browser solves yet another problem

Knowledge Base contains our uploaded/static company information.

But sometimes the user needs something from the **live web**.

That's where AgentCore Browser comes in.

So remember:

```text
Knowledge Base → our indexed documents

Memory         → past customer information

Code Interpreter → computation

Browser        → live web

Gateway/MCP    → business tools/actions
```

That's the heart of this project.

---

# And AgentCore Runtime?

Right now `main.py` lives on your computer.

But the final agent shouldn't depend on:

```text
Ans's Windows laptop being switched on
```

We'll deploy it to:

**Amazon Bedrock AgentCore Runtime.**

Think of Runtime as the cloud home where the finished agent application executes.

Then:

```text
                    AWS
                     │
              AgentCore Runtime
                     │
                   main.py
                     │
                Strands Agent
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    Gateway       Memory          RAG
       │
       ├── orders
       └── refunds

       + Code Interpreter
       + Browser
```

---

# Now you can see why we haven't completed `main.py`

We're building the organs before assembling the body.

So far:

```text
Order backend       ✅
Refund backend      ✅
Order API structure ✅

Gateway             ❌
MCP                  ❌
Memory               ❌
Knowledge Base       ❌
Code Interpreter     ❌
Browser              ❌
Agent assembly       ❌
Runtime deployment   ❌
```

We're not behind. This is the planned construction order.

---

# The engineering method we're going to use

From now on I want **you to make some of the decisions**, rather than copying commands.

Before each step I'll give you a tiny problem.

For example, our next problem is:

> We created API Gateway resources and methods. But are they currently ready to receive normal external requests through a deployed stage?

Instead of immediately handing you five commands, I'll explain the system and ask you what you think should happen next.

You'll answer—even if you're unsure.

Then I'll correct or refine your reasoning.

Then we'll design the action.

Then I'll give you the exact command.

You'll execute it.

Then we'll read AWS's response together.

So the cycle becomes:

```text
UNDERSTAND
    ↓
THINK
    ↓
PREDICT
    ↓
PLAN
    ↓
EXECUTE
    ↓
OBSERVE
    ↓
EXPLAIN RESULT
    ↓
NEXT STEP
```

That's much closer to actually learning engineering.

And when code appears, we're not going to blindly paste 50 lines. We'll discuss what the important pieces mean, such as:

```python
def lambda_handler(event, context):
```

What is `def`?

What is a function?

What is `event`?

What is `context`?

Who calls it?

What goes in?

What comes out?

Why does AWS require this structure?

Then you'll implement/run it.

We can go from kindergarten-simple explanations to the professional terminology immediately afterward, so you learn **both the intuition and the vocabulary**.

---

# Let's start that method right now

We are currently here:

```text
Internet/client
       │
       ?
       ▼
CustomerSupportOrderAPI
       │
       ├── GET /orders/{order_id}
       ├── GET /customers/{customer_id}
       └── GET /customers/{customer_id}/orders
                │
                ▼
          order-tracker
```

We've **constructed** the API resources, methods and integrations.

Our next task is to make/test a deployed API stage.

Before I give you the command, I want you to think.

Imagine you're editing a website. You make changes in the editor, but haven't pressed **Publish** yet.

**Question:** Do you think customers should already be able to use those new changes publicly, or should there be a separate **deploy/publish** step?

There is no penalty for a wrong answer. Tell me what you think happens, and **why**. Then we'll continue the actual build from there.



