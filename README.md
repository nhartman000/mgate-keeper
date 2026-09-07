# MGate Keeper

**MGate Keeper** is a small reproducibility/control experiment for applying structured G8SON gate requirements and GST context to LLM requests and recording the resulting runs for audit.

It is part of the broader MG8 research stack, but it is **not** the canonical definition of the MG8 file formats. The current format baselines live in the dedicated `mg8`, `gst`, `g8son`, and `qson` repositories.

## What this repository actually does

`MGateKeeper` can:

- load a `.mg8` experiment/project file;
- resolve referenced resources relative to that project file;
- load earlier single-gate G8SON demo files and canonical multi-gate G8SON files;
- load GST context/constraint data;
- inject the active GST context and G8SON requirements into the model request;
- use a fixed seed and `temperature=0` for reproducibility experiments;
- record experiment/audit output.

The repository does **not** claim that an external stochastic model becomes mathematically deterministic. Identical responses are measured observations under a fixed model/configuration, not a universal guarantee.

## Architecture

```text
.mg8 experiment/project
        ↓
resolve relative resources
        ├── .gst context / constraints
        └── .g8son gate requirements
        ↓
build bounded control message
        ↓
model request
        ↓
response comparison / experiment
        ↓
audit output
```

## Setup

```bash
git clone https://github.com/nhartman000/mgate-keeper.git
cd mgate-keeper
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Set your own `OPENAI_API_KEY` in `.env`.

`MGATE_MODEL` is optional and can override the model declared by an experiment project.

## Demos

The repository currently contains five top-level demos:

```text
demo1_simple.py
demo2_reproducible.py
demo3_thinking.py
demo4_gates.py
demo5_audit.py
```

The primary reproducibility experiment is:

```bash
python demo2_reproducible.py
```

It loads:

```text
mgate_keeper/projects/photosynthesis.mg8
```

and uses the associated GST/G8SON resources.

## Important implementation note

Earlier versions of this repository accepted `gates` and `context` arguments in `query()` but did not actually place them into the model request. That defect has been corrected: the loaded GST constraints and G8SON requirements are now serialized into the control message sent with the request.

Project-relative paths are also resolved relative to the `.mg8` project file rather than the shell's current working directory.

## Reproducibility versus determinism

The experiment uses several controls that can reduce variation:

- fixed project configuration;
- fixed prompt;
- fixed gate requirements;
- fixed GST context;
- fixed seed where supported by the provider;
- `temperature=0`.

The correct measured statement is therefore:

> Under a fixed control profile, compare repeated model outputs and record whether identical responses occur.

It is not:

> The model is guaranteed to return the same output forever.

## Relationship to the canonical MG8 family

```text
.gst    state / context / constraints
.g8son  bounded conditional gate definitions
.ork    orchestration / routing
.qson   execution and audit trace
.mg8    bounded execution unit/container
.mg8pk  package/composition layer
```

MGate Keeper is an experimental runtime/profile that consumes part of this architecture.

## Security

- Never commit real API keys.
- `.env` is ignored.
- The example environment file contains no key-shaped credentials.
- Generated Python caches/build metadata are not source and should not be committed.

## Status

Research/demo implementation. The repository is useful for reproducibility experiments and interface validation; it should not be presented as formal proof of deterministic LLM behavior.
