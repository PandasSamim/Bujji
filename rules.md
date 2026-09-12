# Project Rules & Guidelines

These mandatory rules govern every step and phase of building **Bujji** (JARVIS-inspired Personal AI Assistant):

## 1. Mandatory Working Rules (Strict Compliance)

1. **Living Core Documentation**:
   Always maintain and continuously update the three core markdown files:
   - [`rules.md`](file:///c:/Users/asami/DOCS/Bujji/rules.md): Project rules, guidelines, architectural invariants, and constraints.
   - [`outline.md`](file:///c:/Users/asami/DOCS/Bujji/outline.md): Full development roadmap (Phases 1-7), architecture, and component directory layout.
   - [`handoff.md`](file:///c:/Users/asami/DOCS/Bujji/handoff.md): Current operational status, completed tasks, verification outcomes, and next action items.

2. **Isolated Scratchpad & Testing Directory (`.antigravity/`)**:
   - The `.antigravity/` folder exists at the project root and MUST remain strictly ignored in [`.gitignore`](file:///c:/Users/asami/DOCS/Bujji/.gitignore).
   - Place **all** testing files, execution verification scripts, helper tools, benchmarks, experiments, and temporary scratch files **exclusively inside `.antigravity/`**.
   - Never put test or scratch files in the main project tree (`bujji/`).

3. **Clean & Sorted Project Structure**:
   - Keep the project root and subdirectories clean, modular, and systematically organized.
   - Maintain clear separation of concerns across core modules (`core`, `tools`, `voice`, `system`, `memory`, `ui`).

4. **Continuous Git Versioning**:
   - Keep the repository connected to Git with proper, atomic, and informative commits corresponding to each phase or logical milestone.
   - Verify that working tree is clean and no unintended artifacts or credentials are committed.

5. **Safety Confirmation for Dangerous Actions**:
   - Any system actions that modify user files, execute destructive commands, or perform sensitive OS operations must include confirmation safeguards.
