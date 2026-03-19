# Family Orchestration Contract

Read this reference when a capability family needs more than a one-shot leaf action.

If the family also uses `EXTEND.md` defaults or workspace-local `.baoyu-skills/.../EXTEND.md` materialization, also read `extend-ownership-contract.md`.

Use this model whenever a request family has one or more of these traits:

- input normalization before execution
- routing between multiple target deliverables or specialized skills
- bridge or normalization steps that must run before the final capability
- intermediate artifacts that may be reviewed, reused, or regenerated
- a first-pass output that should be reviewed before broad regeneration

## Three Roles

### 1. Family Pipeline

The family pipeline is the request-level orchestrator for one capability family.

It owns:
- deciding whether the request belongs to this family
- choosing the target branch or deliverable inside the family
- establishing a working location when intermediate artifacts are needed
- deciding which artifacts need stable cross-skill paths
- invoking bridge skills before the final leaf capability when required
- stopping after first-pass output for review before broad regeneration

It does not automatically own cross-document or cross-project shared state unless that family explicitly includes a workspace-level orchestrator.

### 2. Bridge

A bridge skill converts high-level intent into explicit artifacts that downstream skills can execute.

Examples:
- style brief -> style authority
- theme -> writing posture
- shared constraints -> patched prompt or config files

A bridge:
- consumes explicit inputs
- writes explicit artifacts
- may patch target files inside the current working location
- does not own family sequencing, root working-location policy, or shared bundle persistence

### 3. Leaf Capability

A leaf capability executes one concrete action.

Examples:
- render an image from prompt files
- convert markdown to HTML
- compress images
- fetch a URL and save markdown

A leaf:
- consumes explicit inputs or saved artifacts
- may create its own internal files under the current working location
- does not own family routing, shared state policy, or broad regeneration policy

## Entry Rules

- Enter through the family pipeline when the request is non-trivial for that family.
- Call a leaf directly only when the task is a true one-shot action with no meaningful routing, bridge step, or reusable intermediate artifacts.
- If a family already has both a workspace-level orchestrator and a request-level pipeline, use the request-level pipeline for isolated family work and the workspace-level orchestrator only for broader cross-deliverable coordination.

## Working Location

If the flow has intermediate artifacts, also read `working-artifact-contract.md`.

The family pipeline owns the root working location for the current request unless a higher-level workspace orchestrator already owns it.

## Recommended Sequence

1. Normalize inputs.
2. Choose the family branch or target deliverable.
3. Materialize intermediate artifacts needed by the family.
4. Run bridge skills before the final leaf capability when needed.
5. Invoke the leaf capability.
6. Review the first pass before broad regeneration.
7. Either stop, regenerate selectively, or hand off upward.

## Design Rules

- Do not let a leaf capability become the accidental entrypoint for every non-trivial family request.
- Do not make a bridge skill own family sequencing just because it runs early.
- Do not use unsaved chat context as the only copy of reusable intermediate artifacts.
- Prefer one family pipeline per coherent capability family over repeating ad hoc sequencing rules across multiple leaf skills.
- A family pipeline may route to one leaf or many leaves; the important part is that sequencing and review policy live there rather than leaking into the leaves.
