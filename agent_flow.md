# Agent Code Flow

Here is a high-level visualization of the `agent.py` logic:

```mermaid
flowchart TD
    Start([Start Agent]) --> Init[Initialize Messages<br/>(System Prompt + User Task)]
    Init --> Loop{While True}
    Loop --> LLM[Call OpenAI API]
    LLM --> Parse[Parse JSON Response]
    Parse --> Check{Action Type}
    
    Check -- "done" --> Stop([Finish])
    Check -- Tool Call --> Exec[Execute Tool<br/>(read_file, write_file, bash, etc.)]
    
    Exec --> Output[Capture Output]
    Output --> Append[Append Output to History]
    Append --> Loop
```
