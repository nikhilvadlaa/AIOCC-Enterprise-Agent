# AIOps Competition - Video Script (3 Minutes)

**Goal**: Win the "Pitch" and "Implementation" categories by showing value, advanced AI, and safety.

| Time | Visual (What to Show) | Audio (What to Say) |
| :--- | :--- | :--- |
| **0:00 - 0:30** | **The Problem** | |
| 0:00 | **[Face Camera]** or **[Slide: "The SRE Burnout"]**<br>Show a collage of PagerDuty alerts, Slack noise, and tired engineers. | "Hi, I'm [Name]. Every SRE knows the pain: waking up at 3 AM for a 'High Latency' alert, digging through logs, and realizing... it's just a memory leak we fixed last week." |
| 0:15 | **[Slide: "The Gap"]**<br>Text: *Alerts are easy. Remediation is hard.* | "Monitoring tools tell you *what* is wrong, but they don't fix it. We spend 80% of our time on repetitive manual fixes. That's why I built **AIOCC**." |
| **0:30 - 1:00** | **The Solution & Architecture** | |
| 0:30 | **[Screen: Architecture Diagram]**<br>Zoom in on the Mermaid diagram from README. | "AIOCC is an **Enterprise AIOps Control Center**. It's not just a chatbot; it's a multi-agent system powered by **Google Gemini**." |
| 0:45 | **[Screen: Highlight 'RAG' & 'Human-in-the-Loop']**<br>Mouse over the 'Knowledge Base' and 'Slack' nodes. | "It features specialized agents for Root Cause Analysis and Execution. But unlike standard bots, it has **Long-term Memory** via RAG, and it keeps humans in the loop for safety." |
| **1:00 - 2:15** | **The Demo (The "Money Shot")** | |
| 1:00 | **[Screen: VS Code Terminal]**<br>Run `python run_cycle.py`. Text scrolls rapidly. | "Let's see it in action. I'm simulating a 'Checkout Latency' incident. Watch the agents work." |
| 1:15 | **[Screen: Zoom in on Log]**<br>Highlight: `[RootCauseAgent] Found similar past incident: INC-001` | "Right here—the Root Cause Agent didn't guess. It queried its **Knowledge Base** and found we solved this exact issue last month by restarting the payment connector." |
| 1:30 | **[Screen: Slack App]**<br>Show the message appearing: *⚠️ Approval Required: Restart Server* | "Now, because 'Restarting a Server' is high-risk, the Action Agent pauses. It sends an **Interactive Request** to Slack." |
| 1:45 | **[Screen: Slack App]**<br>Move mouse to click the green **[Approve]** button. | "I get the context, I see the reasoning, and I click **Approve**. Only then does the agent execute the fix." |
| 2:00 | **[Screen: Terminal]**<br>Show `Action Executed: restart_server` and `Incident Resolved`. | "And just like that, the system is back online. No 3 AM wake-up call needed." |
| **2:15 - 2:45** | **The Build (Technical Deep Dive)** | |
| 2:15 | **[Screen: Code - knowledge_base.py]**<br>Scroll through the `search` function. | "I built this using Python and the **Vertex AI SDK**. The RAG system uses semantic search to retrieve past incidents..." |
| 2:30 | **[Screen: Code - action_executor_agent.py]**<br>Show `_send_approval` method. | "...and the Slack integration uses Block Kit for real-time interactivity. It's fully containerized on **Google Cloud Run** for enterprise scale." |
| **2:45 - 3:00** | **Conclusion** | |
| 2:45 | **[Face Camera]** or **[Slide: "AIOCC: The Future of Ops"]** | "AIOCC turns your runbooks into autonomous agents. It combines the reasoning of Gemini with the safety of human oversight. Thanks for watching." |

---

## Preparation Checklist
1.  **Clean your Desktop**: Close unrelated tabs.
2.  **Font Size**: Increase VS Code font size (Ctrl +) so code is readable on video.
3.  **Pre-run**: Run the `test_new_features.py` script once before recording to make sure the "Similar Incident" log appears clearly.
4.  **Slack**: Have the Slack window open side-by-side with your terminal for the "Demo" section.
