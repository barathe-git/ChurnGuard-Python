# ChurnGuard Prompt Architecture

This directory contains all prompt templates used by ChurnGuard's AI agents. All prompts are externalized from code into separate text files for easier maintenance and customization.

## Prompt Files Overview

### 1. CSV Analysis Agent (`csv_to_llm.py`)

#### `churn_analysis_system_prompt.txt`
- **Purpose**: System-level instructions for analyzing customer CSV data and predicting churn
- **Usage**: Loaded once during processor initialization
- **Contains**:
  - Role definition and analysis framework
  - Churn prediction methodology and risk scoring algorithm
  - Required JSON output format specification
  - Analysis instructions and response requirements

#### `csv_analysis_user_prompt_template.txt`
- **Purpose**: Template for structuring the CSV data and analysis request
- **Usage**: Dynamically filled with CSV data for each analysis
- **Variables**:
  - `{csv_text}`: Converted DataFrame with statistics
- **Contains**:
  - Data section header
  - Analysis instructions
  - JSON formatting reminders
  - Output section marker

**How it works:**
```python
# 1. Convert DataFrame to text
csv_text = self._dataframe_to_text(csv_data)

# 2. Fill template with CSV data
user_prompt = user_prompt_template.format(csv_text=csv_text)

# 3. Combine system prompt and user prompt
prompt = f"{system_prompt}\n\n{user_prompt}"
```

### 2. Natural Language Query (NLQ) Chat Agent (`nlq_direct.py`)

#### `nlq_system_prompt.txt`
- **Purpose**: Defines the NLQ agent's role, capabilities, and response guidelines
- **Usage**: Included in every chat query
- **Contains**:
  - Agent role and data sources
  - Analysis capabilities
  - Response guidelines (data-driven, context-aware, specific, etc.)
  - Example analysis areas

#### `nlq_user_prompt_template.txt`
- **Purpose**: Template for structuring user queries with context and conversation history
- **Usage**: Dynamically filled with variables for each query
- **Variables**:
  - `{context}`: Statistical summary of customer data
  - `{conversation_history}`: Previous conversation messages (last 6)
  - `{question}`: Current user question
- **Contains**:
  - Data summary section
  - Conversation history section
  - Current question section
  - Specific instructions for answering

**How it works:**
```python
# 1. Build conversation context from history
conversation_context = ""
if conversation_history:
    conversation_context = "\n**Previous Conversation:**\n"
    for msg in conversation_history[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation_context += f"{role}: {msg['content']}\n"

# 2. Fill template with variables
user_prompt = user_prompt_template.format(
    context=self.context,
    conversation_history=conversation_context,
    question=question
)

# 3. Combine system prompt and user prompt
full_prompt = f"{system_prompt}\n\n{user_prompt}"
```

## CSV Files in System Context

### Question: Can CSV files be included in the system context?

**Answer: YES!** The NLQ agent already implements this approach.

### How it Works:

1. **CSV Upload to GenAI**:
   ```python
   # Upload CSV content to Google AI
   csv_file_obj = io.BytesIO(csv_content)
   csv_file_obj.name = "customer_data.csv"
   uploaded_file = genai.upload_file(csv_file_obj, mime_type="text/csv")
   ```

2. **Include Both Prompt and CSV in Request**:
   ```python
   # Generate response with both prompt and CSV file
   response = model.generate_content([full_prompt, uploaded_file])
   ```

### Benefits:

✅ **Direct Data Access**: LLM can read the entire CSV file directly  
✅ **No Token Limits**: CSV is uploaded separately, not consuming prompt tokens  
✅ **Better Analysis**: LLM can perform calculations and analysis on raw data  
✅ **Context Awareness**: Combines structured data (CSV) with conversational context  

### Two-Tier Context Strategy:

```
┌─────────────────────────────────────────────────────────┐
│                    System Prompt                        │
│  (Role, capabilities, guidelines - from text file)      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   User Context                          │
│  • Data Summary (statistics)                            │
│  • Conversation History (last 6 messages)               │
│  • Current Question                                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   CSV File Upload                       │
│  (Full customer data - uploaded to GenAI)               │
└─────────────────────────────────────────────────────────┘
```

## Customizing Prompts

### Best Practices:

1. **Keep prompts modular**: Separate system context from user context
2. **Use templates**: Utilize variables (`{variable}`) for dynamic content
3. **Version control**: Track prompt changes in git
4. **Test thoroughly**: Changes to prompts can significantly affect AI behavior
5. **Document changes**: Note why prompts were modified

### Modifying Prompts:

1. Edit the relevant `.txt` file
2. No code changes needed - prompts are loaded at runtime
3. Restart the application to load new prompts
4. Test with various queries to ensure quality

### Adding New Prompts:

1. Create a new `.txt` file in `resources/prompts/`
2. Load it in your agent's `__init__` method:
   ```python
   def _load_custom_prompt(self):
       prompt_file = "resources/prompts/your_prompt.txt"
       if os.path.exists(prompt_file):
           with open(prompt_file, 'r', encoding='utf-8') as f:
               self.custom_prompt = f.read()
   ```
3. Use it in your agent's logic

## Conversation History Management

The NLQ agent maintains conversation continuity by:

1. **Limiting History**: Only last 6 messages to avoid token limits
2. **Clear Formatting**: Prefixes each message with "User:" or "Assistant:"
3. **Context Integration**: Combines history with current question seamlessly
4. **Smart Reference**: Instructions encourage the AI to reference previous exchanges

### Example Conversation Flow:

```
User: "How many high-risk customers do we have?"
Assistant: "Based on the data, you have 150 high-risk customers..."

User: "What's their average spend?"
Assistant: "The 150 high-risk customers you asked about have an average spend of $1,234..."
         ↑ References previous context
```

## Troubleshooting

### Prompt Not Loading?
- Check file path is correct relative to project root
- Verify file encoding is UTF-8
- Check file permissions

### CSV Not Included in Request?
- Verify `csv_content` is provided to `load()` method
- Check `uploaded_file` attribute exists
- Review logs for upload errors

### Poor AI Responses?
- Review prompt clarity and specificity
- Check if instructions are too restrictive or too vague
- Verify data context is being built correctly
- Test with simpler prompts to isolate issues

## File Structure

```
resources/prompts/
├── README.md                              # This file
├── churn_analysis_system_prompt.txt       # CSV analysis agent system prompt
├── csv_analysis_user_prompt_template.txt  # CSV analysis agent user template
├── nlq_system_prompt.txt                  # NLQ chat agent system prompt
└── nlq_user_prompt_template.txt           # NLQ chat agent user template
```

## Future Enhancements

- [ ] Add prompt versioning system
- [ ] Create A/B testing framework for prompts
- [ ] Implement prompt performance metrics
- [ ] Add multi-language support
- [ ] Create prompt template library

