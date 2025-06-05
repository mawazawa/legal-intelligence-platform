# Claude API Integration for Unlimited Threads & Persistent Memory

## 🔑 Key Insights: API vs Consumer Claude

### What You CAN Do with API (Not Possible in Consumer Version):

1. **Unlimited Thread Length**
   - No 25-message limit
   - Maintain context across thousands of messages
   - Store conversation history in your own database

2. **Persistent File Memory**
   - Upload files once, reference forever
   - Build knowledge bases that persist across sessions
   - Cross-reference multiple conversations

3. **Temperature Control**
   - Set to 0.0 for deterministic evidence parsing
   - Reduces hallucinations dramatically
   - Consistent outputs for legal documents

4. **Extended Reasoning**
   - Request up to 100,000+ thinking tokens
   - Much deeper analysis than consumer version
   - Better for complex legal reasoning

5. **Batch Processing**
   - Process 1000s of documents in parallel
   - Automated workflows
   - Scheduled analysis

## 💰 Cost Considerations

### Your Claude Max Subscription:
- **Cannot** be used with API
- Only for web/desktop interface
- No programmatic access

### API Pricing (must pay separately):
```python
# Opus 4 pricing as of June 2025
INPUT_COST = 15.00  # per million tokens
OUTPUT_COST = 75.00  # per million tokens

# Example: 50-page legal document
# ~25,000 input tokens + 5,000 output tokens
# Cost: $0.375 + $0.375 = $0.75 per document
```

## 🌡️ Temperature Settings for Evidence Parsing

### Why Zero Temperature Matters:

```python
# Evidence extraction settings
EVIDENCE_SETTINGS = {
    "temperature": 0.0,     # CRITICAL: Deterministic output
    "top_p": 1.0,          # No sampling randomness
    "top_k": 1,            # Always pick most likely token
    "max_tokens": 8192,
    "presence_penalty": 0,  # No creativity boost
    "frequency_penalty": 0  # No repetition penalty
}
```

### Temperature Effects on Hallucinations:

| Temperature | Hallucination Risk | Use Case |
|-------------|-------------------|----------|
| 0.0 | Minimal (~1-2%) | Legal evidence, dates, names |
| 0.1 | Very Low (~3-5%) | Technical facts |
| 0.3 | Low (~5-10%) | Summaries |
| 0.7 | Moderate (~15-25%) | General Q&A |
| 1.0 | High (~30-40%) | Creative writing |

### Real Example:
```python
# Temperature 0.0 - Deterministic
"The contract was signed on March 15, 2024"  # Always same date

# Temperature 0.7 - Variable
"The contract was signed on March 15, 2024"  # Sometimes
"The contract was signed in mid-March 2024"  # Sometimes
"The contract was signed around March 2024"  # Sometimes
```

## 🚀 Quick Start: Claude CLI with Persistent Memory

### 1. Install and Configure:
```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Install CLI
cd legal-intelligence-platform/claude-cli
pip install anthropic tiktoken sqlite3

# Run interactive mode
python claude_persistent_cli.py
```

### 2. Use Evidence Mode:
```bash
# In CLI:
/evidence  # Toggle evidence mode ON
You: Extract all dates from the Johnson contract
Claude: [Temperature 0.0] Found dates: March 15, 2024; April 1, 2024...

/file contracts/johnson_agreement.pdf  # Upload once
You: What are the payment terms?
Claude: [Using uploaded file] Payment terms are Net 30...
```

### 3. Resume Conversations:
```bash
# List previous conversations
python claude_persistent_cli.py
/list

# Resume specific conversation
python claude_persistent_cli.py -c conv_a1b2c3d4
```

## 🧠 Advanced Features Not in Consumer Claude

### 1. Custom System Prompts:
```python
client.messages.create(
    model="claude-opus-4",
    system="""You are a legal evidence analyst.
    CRITICAL RULES:
    1. Never infer information not explicitly stated
    2. Always say "NOT FOUND" if data is missing
    3. Quote exact text with page numbers
    4. Flag any ambiguities immediately
    """,
    messages=[...],
    temperature=0.0
)
```

### 2. Tool Use (Function Calling):
```python
# Define tools for structured extraction
tools = [{
    "name": "extract_contract_terms",
    "description": "Extract structured data from contracts",
    "parameters": {
        "type": "object",
        "properties": {
            "parties": {"type": "array"},
            "dates": {"type": "array"},
            "amounts": {"type": "array"},
            "obligations": {"type": "array"}
        }
    }
}]
```

### 3. Streaming for Real-Time Analysis:
```python
stream = client.messages.create(
    model="claude-opus-4",
    messages=[{"role": "user", "content": "Analyze this deposition..."}],
    stream=True,
    temperature=0.0
)

for chunk in stream:
    print(chunk.content, end="", flush=True)
```

## 📊 Integration with Legal Intelligence Platform

### Connect Claude CLI to Your Debugging Framework:
```python
# In src/core/claude_integration.py
from claude_cli.claude_persistent_cli import ClaudePersistentCLI

class LegalClaudeIntegration:
    def __init__(self):
        self.claude = ClaudePersistentCLI()
        self.conversation_id = self.claude.create_conversation(
            "Legal Document Analysis"
        )
    
    def analyze_with_evidence_mode(self, document_path):
        # Upload document
        file_id = self.claude.upload_file(
            self.conversation_id, 
            document_path
        )
        
        # Analyze with zero temperature
        result = self.claude.chat(
            self.conversation_id,
            f"Extract all monetary amounts and dates from {file_id}",
            evidence_mode=True  # Forces temperature=0.0
        )
        
        return self.parse_structured_output(result)
```

## ⚡ Performance Optimization Tips

### 1. Reuse Conversations:
```python
# Bad: New conversation each time
for doc in documents:
    conv_id = claude.create_conversation()
    result = claude.chat(conv_id, f"Analyze {doc}")

# Good: Reuse conversation with context
conv_id = claude.create_conversation()
for doc in documents:
    result = claude.chat(conv_id, f"Analyze {doc}")
```

### 2. Batch Similar Requests:
```python
# Combine multiple extractions
prompt = """Extract the following from ALL documents:
1. Document 1: [content]
2. Document 2: [content]
3. Document 3: [content]

Return as JSON with document IDs."""
```

### 3. Use Caching for Repeated Queries:
```python
# Cache evidence extraction results
cache_key = hashlib.sha256(f"{document_id}_{query}".encode()).hexdigest()
if cache_key in redis_cache:
    return redis_cache.get(cache_key)
```

## 🔒 Security Considerations

### 1. API Key Management:
```bash
# Never commit API keys
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." >> .env
echo ".env" >> .gitignore

# Use environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### 2. Data Privacy:
- API calls go to Anthropic servers
- Use local models (Llama) for sensitive data
- Consider data residency requirements

### 3. Rate Limiting:
```python
# Implement retry logic
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3)
)
def call_claude_api(prompt):
    return client.messages.create(...)
```

## 📝 Summary

To use Claude API with your Legal Intelligence Platform:

1. **Get API Key**: Sign up at anthropic.com (separate from Claude Max)
2. **Install CLI**: Use provided `claude_persistent_cli.py`
3. **Set Temperature**: Use 0.0 for evidence, 0.7 for general
4. **Upload Files**: Once per conversation, reference forever
5. **Monitor Costs**: ~$0.75 per 50-page document

The API gives you programmatic access, temperature control, and unlimited context that the consumer version doesn't offer. However, it requires separate payment from your Claude Max subscription.
