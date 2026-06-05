# Prompt Engineering Log

## Project: AI Property Triage System

---

# Surface 1 – LangGraph Agent

## Prompt Version 1

Prompt:

Analyze this property listing.

Problem:

Responses were too generic and did not mention market comparison or renovation insights.

Result:

Low-quality recommendations.

---

## Prompt Version 2

Prompt:

Analyze this property listing.
What renovation or condition issues may exist?
Are there similar listings or market insights?

Problem:

Improved recommendations but lacked structure.

Result:

Moderate improvement.

---

## Prompt Version 3 (Final)

Prompt:

Analyze this property listing.

Provide:

1. Property condition observations
2. Possible renovation concerns
3. Market comparison considerations
4. Publication recommendation

Result:

More consistent and structured recommendations.

Selected Version:
Version 3

---

# Surface 2 – Real Estate Assistant

## Prompt Version 1

Prompt:

You are a helpful assistant.

Problem:

Answered unrelated questions.

---

## Prompt Version 2

Prompt:

You are a real estate assistant.
Answer only real-estate-related questions.

Problem:

Still occasionally provided unsupported investment advice.

---

## Prompt Version 3 (Final)

Prompt:

You are a helpful real estate assistant.

Answer only questions related to:

* property listings
* property condition
* renovation advice
* listing preparation

Do not provide legal advice.
Do not guarantee profits.

Result:

More reliable domain-focused responses.

Selected Version:
Version 3

---

# Surface 3 – Guardrails

## Iteration 1

Checks:

* Minimum length

Problem:

Spam content still passed.

---

## Iteration 2

Added:

* Spam keyword detection

Problem:

Off-topic content still passed.

---

## Iteration 3 (Final)

Added:

* Spam detection
* Real-estate keyword validation
* Offensive content detection
* Unsafe output claim detection

Result:

Significantly reduced invalid submissions.

Selected Version:
Iteration 3

---

# Surface 4 – RAG Retrieval

## Prompt Version 1

Query:

Property description only

Problem:

Retrieved less relevant listings.

---

## Prompt Version 2 (Final)

Query:

Property description plus property attributes and location.

Result:

Improved retrieval quality and relevance.

Selected Version:
Version 2

---

# Surface 5 – Property Quality Scoring

## Version 1

Factors:

* Description length

Problem:

Too simplistic.

---

## Version 2 (Final)

Factors:

* Location present
* Property type present
* Images present
* Bathroom information
* Price information
* Description quality

Result:

Produced more realistic listing quality scores.

Selected Version:
Version 2

---

## Summary

Prompt engineering was applied across:

* LangGraph Agent
* Real Estate Assistant
* Guardrails
* RAG Retrieval
* Quality Scoring

Each component underwent iterative refinement to improve reliability, relevance, and usability.
