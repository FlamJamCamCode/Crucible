# Detailed Summary of "Inconsistency Robustness"

## Introduction
"Inconsistency Robustness" (2015, edited by Carl Hewitt and John Woods, Studies in Logic, Volume 52, College Publications, 535 pages) introduces the field of Inconsistency Robustness (IR), founded by Carl Hewitt. IR focuses on information system performance in environments with pervasive, continual inconsistencies, shifting from traditional paradigms that deny or eliminate contradictions. The book, divided into Mathematical Foundations, Software Foundations, and Applications, includes revised papers from the 2011 and 2014 International Symposia on Inconsistency Robustness at Stanford. Hewitt contributes chapters on formalizing common sense, IR in mathematics, the Actor Model, logic programs, and ActorScript. Other chapters apply IR to diverse fields like law, ontologies, and biology.

## Key Points and Concepts
- **Definition of IR**: Information system performance amidst continual inconsistencies, treating contradictions as opportunities for explicit pro/con argumentation and progressive resolution, avoiding classical logic’s "ex falso quodlibet" (explosion on contradiction).
- **Paradigm Shift**: Unlike "inconsistency denial" (assuming consistency) or "inconsistency elimination" (removing contradictions), IR embraces robust management of inconsistencies, critical for large-scale systems like the Internet.
- **Core Principle**: Formalize contradictions explicitly to enable robust reasoning without system collapse.
- **Historical Context**: Mathematics has historically repaired contradictions (e.g., Russell’s Paradox) progressively, informing IR’s approach.
- **Interdisciplinary Applications**: IR applies to mathematics, software, logic programs, legal reasoning, ontologies, linguistics, biology, chemistry, and the technological singularity.
- **Inconsistency as a Feature**: Sometimes inconsistency is a feature, particularly when considering human constraints about ground truths and what ought to be or is the state from interpolating between those ground truths. Access to ground truths may also vary significantly, making inconsistency not just inevitable but a necessary feature of many systems. This aligns with IR's emphasis on embracing rather than eradicating inconsistencies, allowing systems to reflect real-world complexities where absolute consistency is unattainable due to subjective interpretations, limited data, or evolving contexts.

## Problems Addressed
IR tackles pervasive inconsistencies across domains, worsened by scale and complexity:

### Mathematical Foundations
- **Problem**: Classical logic fails in inconsistent environments; historical paradoxes (e.g., set theory) show foundations must tolerate contradictions without collapse.
- **Impact**: Traditional systems assuming consistency are fragile, ignoring mathematics’ iterative repair process.

### Software and Computation
- **Problem**: Large-scale systems (e.g., Internet) face continual inconsistencies from distributed data, concurrency, and errors.
- **Impact**: Fragility in scalability, privacy, security, and anti-cloud paradigms.

### Logic Programs
- **Problem**: Issues like the contrapositive inference bug (invalid deductions from contradictions) and negation as failure cause unreliable reasoning.
- **Impact**: Historical logic programming issues (e.g., Prolog) highlight recurring IR challenges.

### Applications
- **Legal Reasoning**: Inconsistencies in judge-made laws and language paradoxes distort decisions.
- **Ontologies and Knowledge Systems**: Uncertainty from subjective experts, incomplete data, and integration errors reduces reliability.
- **Biology, Chemistry, Linguistics**: Complex, imprecise data creates modeling inconsistencies.
- **General**: Ignoring inconsistencies lowers reliability, interoperability, and distorts processes, with environmental/economic consequences.

## Solutions Offered
IR provides a framework with specific tools:

- **Direct Logic™**:
  - Robust to inconsistencies, avoiding explosion.
  - Fixes contrapositive inference bug.
  - Supports direct argumentation and inference for scalable, natural language reasoning.
- **Actor Model**:
  - Concurrent, message-passing entities handle inconsistencies.
  - Used in industry (e.g., eBay, Microsoft, Twitter).
  - Supports iAdaptive concurrency for privacy/security.
- **ActorScript™**:
  - Extends languages like C#, Java for IR implementation.
- **Logic Programs**:
  - Make inconsistencies explicit; evolve programs progressively.
- **Applications**:
  - Probabilistic extensions and meta-level confidence for ontologies.
  - Consistency repair methods.
  - Uncertainty-aware frameworks for law, biology, etc.
- **General Methods**:
  - Formalize common sense for integration.
  - Use sociological bases for foundations.
  - Attach meta-information for reliability.

## Alternative Tradeoffs
IR contrasts with traditional approaches, presenting tradeoffs:

- **Denial vs. Robustness**:
  - Denial: Assumes consistency (simpler, fragile).
  - IR: Accepts inconsistencies (complex, scalable, reliable).
- **Elimination vs. Management**:
  - Elimination: Removes contradictions (effective small-scale, impractical at scale).
  - IR: Manages via argumentation (progressive, needs new tools).
- **Classical vs. Paraconsistent Logic**:
  - Classical: Explodes on contradiction (predictable, unusable in inconsistency).
  - Paraconsistent (e.g., Direct Logic): Tolerates contradictions (flexible, risks unresolved debates).
- **Centralized vs. Distributed Models**:
  - Centralized: Assumes consistency (easier reasoning, brittle).
  - Actor Model: Distributed (handles inconsistencies, complex concurrency/privacy).
- **Absolute Consistency vs. Progressive Repair**:
  - Absolute: Ideal but unattainable.
  - IR: Ongoing repairs (realistic, needs iterative processes).
- **Applications**:
  - Ontologies: Strict consistency reduces usability; IR’s probabilistic methods improve reliability but add overhead.
  - Law: Ignoring paradoxes corrupts processes; IR formalizes them but requires effort.

IR prioritizes resilience over simplicity, optimizing performance in inconsistent environments, where inconsistency can serve as a beneficial or essential feature reflecting human and systemic realities.


Then add to it, that sometimes inconsistency is a feature, when considering human constraints about ground truths and what ought or is the state from interpolating between those ground truths.
And the access to ground truths may also be very different.
So inconsistency may be a feature or actually a necessary feature of many systems.