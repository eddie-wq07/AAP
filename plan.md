# Job Application Agent - Project Plan
Built by Eddie Jung | Last updated: May 2026

---

## What We Are Building

An automated job application agent that:
1. Scrapes job postings from Simplify.jobs
2. Auto-applies using Playwright (headless browser automation)
3. Personalizes your resume per job using the Claude API
4. Finds the recruiter's email via Apollo
5. Sends a personalized cold email from the dedicated internship Gmail

---

## Email Strategy

- Dedicated Gmail: edward.internships@gmail.com (secured)
- All application confirmation emails go here, keeping the main inbox clean
- All cold outreach emails to recruiters are sent from this address

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Language | Python | Everything |
| Browser automation | Playwright (Python) | Log into Simplify, fill forms, submit applications |
| AI backbone | Claude API | Resume personalization, email drafting |
| Recruiter finding | Apollo | Find recruiter name and email from company name |
| Email sending | Gmail API / SMTP | Send cold emails from internship Gmail |
| Job source | Simplify.jobs | Job listings to apply to |
| IDE | VS Code | Where you write and run everything |

---

## Project Structure

```
job-agent/
├── scraper/
│   └── simplify_scraper.py       # Playwright: log in, find jobs, extract details
├── applicator/
│   └── form_filler.py            # Playwright: fill application form and submit
├── resume/
│   └── personalizer.py           # Claude API: tweak resume summary per job
├── outreach/
│   ├── recruiter_finder.py       # Apollo: find recruiter email
│   └── email_sender.py           # Gmail: send personalized cold email
├── data/
│   ├── jobs_queue.json           # List of jobs to apply to
│   ├── applied_jobs.json         # Log of completed applications
│   └── edward_resume.pdf         # Base resume
├── .env                          # All credentials, never share or commit this
├── config.py                     # Settings, reads from .env
└── main.py                       # Orchestrator, runs the full pipeline
```

---

## Build Phases

### Phase 1 - MVP: Proof of Concept
- Set up VS Code project and install Playwright
- Write Simplify scraper: log in, find 1 job, extract title, company, description, apply link
- Write form filler: click Apply, fill fields with Eddie's info, submit
- Goal: 1 real application submitted end-to-end

### Phase 2 - Personalization
- Connect Claude API
- Feed job description to Claude, get tailored resume summary and cover blurb
- Attach personalized content during application

### Phase 3 - Recruiter Outreach
- Use Apollo to find recruiter from company name
- Draft personalized cold email via Claude (same style as coffee chat emails)
- Send from edward.internships@gmail.com

### Phase 4 - Scale to 100/day
- Add concurrency: run multiple headless Playwright instances in parallel
- Each worker handles one job at a time, 10-20 workers running simultaneously
- At 10 workers, each taking 3 min per application, that is roughly 100 applications per 5 hour window
- Move project to Mac Mini, set up a daily cron job for hands-free runs
- The MVP architecture already supports this. The only addition is the concurrency layer.

---

## How It Runs (End State)

```
You type: python main.py

Playwright (headless) logs into Simplify
Finds 5-10 relevant jobs
For each job:
  Fills and submits the application form
  Claude personalizes a resume blurb
  Apollo finds the recruiter
  Gmail sends a cold email to recruiter
Script finishes: "Applied to 8 jobs, sent 8 emails. Time: 12 min."
```

---

## Headless Configuration

Playwright runs headless by default (no visible browser) so the code is already built for parallel scaling from day one. Toggle visibility with one line in config.py:

```python
HEADLESS = True  # Set to False anytime to watch the browser in action
```

Used in every Playwright script like:

```python
browser = playwright.chromium.launch(headless=config.HEADLESS)
```

---

## Scale Strategy

| Stage | Jobs/Day | Approach |
|---|---|---|
| MVP | 1 | Single headless instance, run manually |
| Early | 5-10 | Single headless instance, run manually each day |
| Scaled | 100 | 10-20 parallel headless workers, Mac Mini cron job |

Note: Applying to hundreds of jobs per day from one account risks bot detection on Simplify. 5-10/day is safe and sustainable. Each application also gets a personalized recruiter email, which most applicants skip. That is the real edge here, not volume.

---

## Cost Estimate (Per Day, 10 Jobs)

| Service | Estimated Cost |
|---|---|
| Claude API (resume + email, ~1k tokens x 10) | ~$0.03-0.06/day |
| Apollo credits (recruiter lookup x 10) | Depends on plan |
| Gmail API | Free |
| Total | Virtually free at this scale |

---

## Credentials and Connectors

Never share credentials in chat. All sensitive info lives in a .env file on your machine only.

Create a .env file in the project root:

```
SIMPLIFY_EMAIL=edward.internships@gmail.com
SIMPLIFY_PASSWORD=yourpassword
CLAUDE_API_KEY=sk-ant-...
APOLLO_API_KEY=...

```

How each service connects:

| Service | How |
|---|---|
| Simplify | Email and password in .env, Playwright logs in like a human |
| Claude API | API key from console.anthropic.com, paste into .env |
| Apollo | API key from Apollo dashboard, paste into .env |
| Gmail | One-time Google OAuth setup, done once |

No one-click connect buttons like Cowork. Each service is set up manually once, then scripts connect automatically on every run. After setup, everything runs with:

```bash
python main.py
```

---

## Setup Checklist

- [ ] Simplify.jobs account with resume uploaded
- [x] edward.internships@gmail.com created
- [ ] Claude API key (console.anthropic.com)
- [x] Apollo account
- [x] Python installed
- [x] VS Code installed
- [ ] Playwright installed (pip install playwright && playwright install chromium)
- [ ] .env file created with all credentials

---

## First Thing We Build

simplify_scraper.py - Playwright logs into Simplify, finds one job, prints the title, company, and application link to the terminal. Everything else builds on top of this.

---
