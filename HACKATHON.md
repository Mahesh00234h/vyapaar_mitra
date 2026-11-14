# Vyapaar Mitra

## One-line pitch

Vyapaar Mitra is an autonomous growth analyst for Paytm merchants. It finds revenue
opportunities in a shop's own transaction history, asks the merchant for approval in
Hindi, runs the approved campaign, and measures whether it actually worked.

Built for the Paytm Build for India AI Hackathon, Pune Edition, Track 1, Merchant Growth
AI, by Mahesh Rakte and Prajwal.

## The merchant problem

A small merchant knows whether today felt busy, but does not have time to analyse months
of transactions. Important signals stay hidden:

- regular customers quietly stop returning
- a particular weekday or time slot is consistently slow
- customers buy tea but rarely add a snack
- a discount may increase sales while losing money
- a campaign may look successful without proving that it caused the result

Large businesses solve these problems with analysts, marketers, experimentation platforms,
and data teams. A small shop usually has none of those resources.

## What Vyapaar Mitra solves

Vyapaar Mitra turns the merchant's transaction history into a controlled growth loop:

1. **Triage:** arithmetic identifies lapsed regulars, off-peak gaps, and basket gaps.
2. **Generate:** the language model proposes open-ended actions and writes merchant-facing
   Hindi or Hinglish. It does not create financial numbers.
3. **Simulate:** code prices each action at multiple discount levels and rejects actions
   that violate margin, budget, or profit guardrails.
4. **Approve:** the merchant hears a short Hindi explanation and says HAAN or NAHI.
5. **Dispatch:** approved campaigns use an 85 percent treatment group and a 15 percent
   random holdout group.
6. **Measure:** after 72 hours, lift is calculated as treated conversion minus control
   conversion.
7. **Learn:** the measured result is written to campaign memory so future predictions
   improve.

## Why this is more than a recommendation engine

A recommendation engine stops after suggesting an action. Vyapaar Mitra completes the
operating loop:

- it explains why the opportunity is worth attention
- it protects the merchant from negative-profit offers
- it requests approval before spending the merchant's budget
- it executes a controlled experiment
- it reports measured lift, not a model's promise
- it learns from the result

The key design rule is simple: **the language model never produces a number**. Financial
figures, holdout assignment, profit checks, and measured lift are owned by deterministic
code.

## How the demo works

The demo uses one synthetic tea-stall ledger with 400 customers and 18 months of
transactions. The data includes weekday patterns, a dead Tuesday afternoon, festival
spikes, messy item names, and a cohort of regulars who have lapsed.

The dashboard shows:

1. the opportunity detected tonight
2. the reasoning trace and ranked candidates
3. the Hindi merchant approval script
4. personalised treated messages and the held-out control group
5. expected versus measured campaign value
6. the learning curve across campaigns

The local soundbox is the reliable demo voice channel. It plays the same Sarvam-generated
Hindi script in a browser and accepts either microphone speech or the HAAN and NAHI
buttons. The upstream logic is shared with the planned telephony adapter.

## How a merchant uses it

1. The merchant connects Paytm transaction history and sets a monthly offer budget.
2. Vyapaar Mitra checks the shop each night.
3. If no opportunity clears the guardrails, it stays silent.
4. If an opportunity is worthwhile, the merchant receives a short approval call.
5. The merchant says HAAN to approve or NAHI to decline.
6. Vyapaar Mitra sends the approved offer to the selected treatment group.
7. The merchant sees the result after the measurement window.
8. The next campaign uses the shop's accumulated evidence.

In production, Paytm would handle customer identity, consent, frequency caps, opt-out
rules, and message delivery. The merchant approves a strategy, not a customer list.

## Suggested judge explanation

### 30 seconds

"Small merchants have transaction data but no analyst. Vyapaar Mitra finds patterns such
as lapsed regulars and dead time slots, proposes a campaign in the merchant's language,
and asks for approval before acting. The important part is that the AI never invents the
money. Deterministic code calculates profit, a random holdout measures true lift, and
the result improves the next decision."

### 90 seconds

"Here is a tea stall with 400 customers. The system has found twelve regulars who stopped
coming and a monthly value at risk. It generated several possible actions, but the
simulator rejected the ones that lose money and selected the profitable winback action.
The merchant hears the offer in Hindi and says HAAN. The system sends personalised
messages to 85 percent of the target segment and deliberately holds back 15 percent.
After 72 hours, it compares conversion in the two groups. That difference is the real
campaign lift, not a model estimate. The learning curve shows that the system's belief
gets closer to the shop's observed response over repeated campaigns. If there is no
profitable action, it does nothing."

## Strong answers to likely questions

**What does it cost at scale?**  
Triage is arithmetic and can run for every merchant. Only merchants crossing the
opportunity threshold use the language model and voice layer.

**Why should a merchant trust it?**  
The merchant approves before dispatch. Offers have margin and budget guardrails, every
decision is logged, and results are measured against a control group.

**How do you know the campaign caused the result?**  
The treatment and holdout groups are assigned before dispatch. Lift is treated conversion
minus control conversion.

**What happens with little data?**  
The system starts with a conservative prior and shrinks toward the merchant's own
measured history as campaigns accumulate.

**What is AI doing here?**  
The model resolves messy item names, proposes new campaign ideas, and writes natural
merchant-facing language. It does not decide financial truth.

**What is the production path?**  
Paytm transaction and consent systems would provide the ledger and delivery controls.
Sarvam supplies language and voice, while n8n orchestrates the nightly workflow and the
72-hour measurement wait.
