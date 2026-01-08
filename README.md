# NEXUS

> **Nexus** - the trustworthy domestic brain

**Dominus & Lúcia - The Agents of the Nexus.**

---

## Overview

Nexus is a domestic cognitive system designed to run inside a local homelab: to observe, learn, and act responsibly within a controlled environment. It is not a consumer product; it is a technical ecosystem engineered for security, auditability, and elegant presence.

Nexus manifests through *Lumen* (physical nodes), thinks in the *Cortex*, remembers in *Memory*, researches via the *Oracle*, orchestrates events through the *Stream*, speaks through *Echo*, and is protected by the *Guard*. Dominus and Lucia are the primary agents, each with distinct and complementary roles.

---

## Core principles

1. **Human control always** - autonomy is granted, limited, and revocable.
2. **Observation ≠ action** - perceiving does not imply acting.
3. **Gradual autonomy** - start reactive, evolve to proactive, with boundaries. 
4. **Local by default** - privacy first; external integration only by explicit opt-in.
5. **Everything is auditable** - decisions are logged and explainable.
6. **Elegant presence** - minimal intrusion; contextual communication.

---

## Canonical nomenclature

- **Nexus** — ecosystem / project umbrella
- **Cortex** — thinking core
- **The** Agents — Dominus (technical) & Lucia (human-centric)
- **Lumen** — physical room nodes (microphone + speaker + LED)
- **Memory** — storage (factual, episodic, social, technical)
- **Oracle** — controlled web research module (cache + validation)
- **Stream** — event bus
- **Guard** — authorization, policies, kill-switch
- **Echo** — STT/TTS and voice management

---

# Project goals (high level)

1. Transform Dominus & Lucia into autonomous yet controlled agents.
2. Run locally in a homelab with graceful failure and full auditability.
3. Connect nodes (Lumen) via MQTT/WebSocket with low latency and security.
4. Provide infrastructure for learning: logs, embeddings, and prediction (when appropriate).
5. Enable safe research (Oracle) with caching and source attribution.
6. Define clear social and operational rules for spontaneous initiative.

---

## Architecture (macro view)

```text
[Lumens] -> [Echo STT] -> [Stream] -> [Cortex]
                               |         |
                               v         v
                            [Memory]  [Agents: Dominus/Lúcia]
                               |         |
                             [Oracle] [Guard]
                               v
                            [Executors -> Proxmox / scripts / HA / devices]
```

Quick description:
*Lumens* capture audio and presence, publishing events to the Stream.
*Echo* converts audio to text (STT) and handles voice output (TTS).
*Stream* distributes events to the Cortex and agents.
*Cortex* maintains global state, simulates scenarios, and coordinates.
*Memory* stores facts, episodes, preferences, and logs.
*Agents* (Dominus/Lucia) read state and propose actions.
*Guard* authorizes or blocks sensitive actions.
*Oracle* performs controlled external research and attaches results to context.

---

## Minimal event schema (JSON)

```json
{
  "type": "speech_detected",
  "timestamp": "2026-01-08T18:20:00-03:00",
  "location": "kitchen",
  "participants": ["ana_paula","vinicius"],
  "transcript": "let's make chocolate cookies",
  "keywords": ["cookie","chocolate"],
  "confidence": 0.92
}
```

Other types: `sensor_temp`, `service_alert`, `user_command`, `presence_change`, `action_proposed`, `action_executed`, `audit_log`.

---

## Global state model (example)

```json
{
  "time": "2026-01-08T18:21:00-03:00",
  "users": {
    "vinicius": {"role": "admin", "prefs": {"sweet": true}},
    "ana_paula": {"role": "user", "allow_interruption": true}
  },
  "house": {"ambient_temp": 29, "people_home": true},
  "server": {"cpu": 67, "ram": 53, "temp": 72},
  "ongoing_contexts": []
}
```

---

## Decision policies (condensed examples)

### Dominus (priority model — YAML)

```yaml
goal: maintain_stability
priorities:
  - keep_critical_services_online
  - avoid_hardware_damage
  - minimize_user_impact
service_rank:
  pihole: 100
  nextcloud: 90
  home_automation: 85
  bazarr: 20
  sonarr: 10
```

### Lucia (social rules — summary)

```yaml
policy:
  interrupt_threshold: 0.8
  allowed_topics_to_interrupt: ["food","safety","urgent_home_issues"]
  min_time_between_suggestions_minutes: 30
  polite_tone: true
```

Rule: Lucia only interrupts if `relevance * permission * context_ok > interrupt_threshold`.

---

## Audio pipeline (standalone)

1. **VAD** (voice activity detection) on Lumen
2. **STT** (prefer local — Whisper local / VOSK / Silero)
3. **NLP**: intent and keyword extraction (spaCy, custom rules)
4. **Evento** published to Stream
5. **Cortex + Agents** decide/propose
6. **Guard** validates
7. **Echo** executes local TTS

---

## Memory & learning

- Start with SQLite for facts and episodes.
- For recall/search: generate embeddings (open-source, local sentence-transformers) and store in FAISS/Chroma.
- Neural networks: used for classification/prediction (CPU spikes, human error likelihood); final decisions remain deterministic.
- Offline training: capture logs, label manual interventions, train batch models.

**Practical rule:** neural models assist prediction and suggestion; they **do not** decide critical actions alone.

---

## Oracle (external research)

- Restrictions: always cache results with metadata (source, time, trust_score).
- Summarize before presenting; store links/sources in Memory.
- Rate-limit and firewall rules to prevent unsupervised crawling.

---

## Security, privacy & governance

- **Sensitive data** stays local by default.
- Lumen ↔ Nexus communication via TLS + mutual auth (MQTT over TLS or mTLS gRPC).
- RBAC authorization (roles: admin, user, guest).
- Physical kill-switch to disable audio input and autonomous actions.
- Immutable logs for critical decisions (write-once, tamper-evident).

---

## Lumen provisioning (suggested hardware)

- ESP32 / ESP32-S3 for simple detection (VAD) and LED signaling
- Raspberry Pi Zero W / 4 for nodes running local STT/TTS
- Quality USB microphone + small speaker
- Communication: MQTT (TLS) or secure WebSocket

---

## Development & contributions

- Standard: automated tests + linting
- Branching: protected `main`, `develop` for integration, feature branches via PR
- Each module defines its event contracts in its README
- Mandatory reviews for changes in `Guard`, `Cortex`, `Memory`, or `Agents`

---

## Practical examples & snippets

- Dominus proposing an action due to high CPU temperature:

```json
{
  "type": "action_proposed",
  "agent": "dominus",
  "proposal": {
    "action": "shutdown_services",
    "services": ["bazarr","sonarr"],
    "reason": "cpu_temp_critical"
  },
  "confidence": 0.98
}
```

- Lucia voice suggestion example:

```json
{
  "type": "suggestion",
  "agent": "lucia",
  "message": "I noticed you were talking about cookies. Would you like a quick recipe?",
  "context_id": "ctx_20260108_1823"
}
```

---

## Code of conduct

All contributions must respect security, privacy, responsibility, and the project philosophy: user safety and auditability always come first.
