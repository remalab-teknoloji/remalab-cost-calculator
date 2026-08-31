# Remalab AI Repair Cost Assistant

This repository contains the Remalab client repair cost calculator plus a conversational AI layer.

## Production deployment

The conversational version requires a server-side environment because the OpenAI API key must never be exposed in browser code. The repository is prepared for Vercel.

1. Import this GitHub repository into Vercel.
2. In the Vercel project, add an environment variable named `OPENAI_API_KEY` with a valid OpenAI API key.
3. Deploy the project.
4. The root URL will serve `ai.html` through `vercel.json`.

The existing GitHub Pages calculator can remain available as the non-AI/static fallback.

## Architecture

- `ai.html`: Remalab branded conversational UI with text and realtime voice.
- `calculator.html`: deterministic Remalab pricing engine and client calculator.
- `api/realtime-token.js`: server-side endpoint that validates the Remalab access code and creates a short-lived OpenAI Realtime client secret.
- `vercel.json`: routes `/` to the AI interface.

The AI assistant never calculates prices. It interprets the client's request, asks clarifying questions when needed, and calls the local calculator through the `configure_quote` tool. The calculator remains the pricing source of truth.
