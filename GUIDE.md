# Getting started with hybrid-agents

This plugin has one skill, `hybrid-agent-orchestrator`. When you call it in Claude Code, a main agent splits the work. It hands coding, writing, figures and repetitive jobs to the agents you chose for them (Claude, Codex, agy, Copilot), then checks the results itself.

## Let an agent set it up for you

Paste this into Claude Code (or another coding agent):

```
Follow https://github.com/K2YOUNG/hybrid-agents-plugin/blob/main/GUIDE.md to install and set up the hybrid-agents plugin for me. Run the commands yourself, and stop and tell me whenever I need to do something.
```

## For AI agents helping a user

If a user gave you this guide, set the plugin up for them in this order:

1. Run the `--version` checks under "What you need". Tell the user which agent CLIs are missing. Don't install them unless the user asks.
2. Run the two commands in Step 1, then `claude plugin list` (Step 2) to confirm `hybrid-agents` is installed.
3. Stop. Ask the user to quit Claude Code and start it again from the same folder with `claude -c`. That reopens this conversation with the plugin loaded. You can't restart your own session.
4. After the restart, suggest a first request such as `/hybrid-agents:hybrid-agent-orchestrator <task>`. The skill asks its setup questions itself. Let the user answer them; don't choose for the user.

Hand these back to the user and wait:

- logging in to Codex, agy or Copilot (these are interactive)
- the restart in step 3
- the setup questions in step 4
- confirming in another agent's own window, when that agent refuses a task passed on by you

Never type a password or token for the user.

## What you need

- Claude Code, installed and logged in
- The CLI of each agent you want to hand work to. You only need the ones you plan to use.
  - Codex CLI (`codex`)
  - Antigravity CLI (`agy`)
  - GitHub Copilot CLI (`copilot`)
- Python 3

Check what is installed. If a version prints, the tool is there.

```
claude --version
codex --version
agy --version
copilot --version
python3 --version
```

herdr is not required.

## Step 1. Install the plugin

Run these two lines in a terminal:

```
claude plugin marketplace add K2YOUNG/hybrid-agents-plugin
claude plugin install hybrid-agents@hybrid-agents
```

If Claude Code was already open, quit and start it again.

## Step 2. Check the install

```
claude plugin list
```

If `hybrid-agents` is in the list, the install worked.

## Step 3. First run: choose the roles

In Claude Code, type the skill name followed by what you want done:

```
/hybrid-agents:hybrid-agent-orchestrator rewrite this repo's README for first-time users
```

The first time, it asks three things before starting the work.

1. **Main agent**: the agent that splits the work and checks the results. The default is whichever agent called the skill (`invoker`).
2. **Who does each job**: pick `claude`, `codex`, `agy` or `copilot` for each.

   | Job | What it covers | Default |
   | --- | --- | --- |
   | `coding` | writing code, fixing bugs | `claude` |
   | `prose` | papers, reports, READMEs and other text | `agy` |
   | `design` | figures, slides, HTML pages | `codex` |
   | `bulk` | repetitive work such as summarizing long logs or generating many tests | `agy` |
   | `review` | a second review of another agent's output | `codex` |

3. **Use running agents?** `ask` asks you each time (the default). `new` always opens a new session.

If you are not sure, answer "use the defaults". Don't give a role to an agent you haven't installed. Your answers are saved to `~/.config/hybrid-agents/config.json`, and it won't ask again.

## Step 4. Pick a running agent

With `ask`, before handing work to another agent it shows the agents that are running now and asks you to pick one. Each entry shows the name, where it runs, its status (`idle`, `working` and so on) and its working folder. The last option is "Start a new session".

- If you pick a running agent, it gets the task inside the conversation it already has.
- If nothing is running, or you said this request should use new sessions, it opens a new session without asking.
- The list comes from agents running in the Herdr app (`hc`) or herdr, and from Claude sessions connected over Remote Control. If you don't use any of these, it always opens new sessions.
- Once you pick an agent, it keeps using that agent for the rest of the request without asking again.
- The agent you pick may refuse and say it needs your confirmation. Some agents are set up not to follow instructions passed on by another agent. Type a short confirmation in that agent's own window.

## Step 5. Get the results

The main agent checks each result before it reports. For code it reads the diff and runs the tests. For text it compares every number and citation with the source files. For figures it renders them and checks the numbers and labels. The final report says who made what, what was checked and what was not.

## Example requests

| Request | Role that does it |
| --- | --- |
| "Fix the login bug" | `coding` |
| "Draft chapter 4 of the paper from the experiment results" | `prose` |
| "Make a bar chart SVG from `results.csv`" | `design` |
| "Summarize every log in `logs/`" | `bulk` |
| "Review these changes once more" | `review` |

When another agent does the writing, the main agent doesn't write the text itself. It hands over a brief and a fact pack (every number with its source), then checks the draft for facts only.

If you name an agent in the request ("let Codex write this one"), that wins over the saved settings, for that request only.

## Change the settings

Ask in Claude Code:

- "In hybrid-agent-orchestrator, change the coding role to codex"
- "I want to set up the hybrid-agent-orchestrator roles again from the start"

Deleting `~/.config/hybrid-agents/config.json` also makes it ask again on the next run.

## Common problems

- **The chosen agent can't be used** (usage limit, expired login, repeated timeouts): the work moves to the next agent in a fixed order. Text goes agy → Codex → Claude, figures go Codex → agy → Claude, and repetitive work goes agy → Codex → Claude.
- **herdr isn't installed**: that's fine. It skips that step and uses one-shot CLI calls or a shared markdown mailbox instead.
- **agy can't write files** (exit code 15): add a `write_file(<folder>)` rule to `permissions.allow` in `~/.gemini/antigravity-cli/settings.json`.

## Update and remove

```
claude plugin marketplace update hybrid-agents
claude plugin update hybrid-agents@hybrid-agents
```

```
claude plugin uninstall hybrid-agents@hybrid-agents
```

To remove your saved roles too, delete `~/.config/hybrid-agents/config.json`.
