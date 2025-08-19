# Dependency Analysis for ProVAI

- **Status:** Completed
- **Date:** 2025-08-19
- **Authors:** @joelabreurojas

---

## 1. Methodology

This analysis was conducted by generating a full dependency tree using the command `uv pip tree`. The goal is to identify any packages that are unusually large, have a high number of transitive dependencies, or may be redundant, in order to keep our final application lean and secure.

---

## 2. Full Dependency Tree

<details>
  <summary><strong>Click to expand the full dependency tree</strong></summary>

  ```text
alembic v1.16.2
├── mako v1.3.10
│   └── markupsafe v3.0.2
├── sqlalchemy v2.0.41
│   ├── greenlet v3.2.3
│   └── typing-extensions v4.14.1
└── typing-extensions v4.14.1
cryptography v45.0.5
└── cffi v1.17.1
    └── pycparser v2.22
email-validator v2.2.0
├── dnspython v2.7.0
└── idna v3.10
fastapi v0.116.0
├── pydantic v2.11.7
│   ├── annotated-types v0.7.0
│   ├── pydantic-core v2.33.2
│   │   └── typing-extensions v4.14.1
│   ├── typing-extensions v4.14.1
│   └── typing-inspection v0.4.1
│       └── typing-extensions v4.14.1
├── starlette v0.46.2
│   └── anyio v4.9.0
│       ├── idna v3.10
│       └── sniffio v1.3.1
└── typing-extensions v4.14.1
fastembed v0.7.1
├── huggingface-hub v0.34.3
│   ├── filelock v3.18.0
│   ├── fsspec v2025.5.1
│   ├── hf-xet v1.1.5
│   ├── packaging v24.2
│   ├── pyyaml v6.0.2
│   ├── requests v2.32.4
│   │   ├── certifi v2025.6.15
│   │   ├── charset-normalizer v3.4.2
│   │   ├── idna v3.10
│   │   └── urllib3 v2.5.0
│   ├── tqdm v4.67.1
│   └── typing-extensions v4.14.1
├── loguru v0.7.3
├── mmh3 v5.1.0
├── numpy v2.3.1
├── onnxruntime v1.22.0
│   ├── coloredlogs v15.0.1
│   │   └── humanfriendly v10.0
│   ├── flatbuffers v25.2.10
│   ├── numpy v2.3.1
│   ├── packaging v24.2
│   ├── protobuf v5.29.5
│   └── sympy v1.14.0
│       └── mpmath v1.3.0
├── pillow v11.3.0
├── py-rust-stemmers v0.1.5
├── requests v2.32.4 (*)
├── tokenizers v0.21.2
│   └── huggingface-hub v0.34.3 (*)
└── tqdm v4.67.1
httptools v0.6.4
langchain-chroma v0.2.5
├── chromadb v1.0.15
│   ├── bcrypt v4.3.0
│   ├── build v1.2.2.post1
│   │   ├── packaging v24.2
│   │   └── pyproject-hooks v1.2.0
│   ├── grpcio v1.73.1
│   ├── httpx v0.28.1
│   │   ├── anyio v4.9.0 (*)
│   │   ├── certifi v2025.6.15
│   │   ├── httpcore v1.0.9
│   │   │   ├── certifi v2025.6.15
│   │   │   └── h11 v0.16.0
│   │   └── idna v3.10
│   ├── importlib-resources v6.5.2
│   ├── jsonschema v4.24.0
│   │   ├── attrs v25.3.0
│   │   ├── jsonschema-specifications v2025.4.1
│   │   │   └── referencing v0.36.2
│   │   │       ├── attrs v25.3.0
│   │   │       └── rpds-py v0.26.0
│   │   ├── referencing v0.36.2 (*)
│   │   └── rpds-py v0.26.0
│   ├── kubernetes v33.1.0
│   │   ├── certifi v2025.6.15
│   │   ├── durationpy v0.10
│   │   ├── google-auth v2.40.3
│   │   │   ├── cachetools v5.5.2
│   │   │   ├── pyasn1-modules v0.4.2
│   │   │   │   └── pyasn1 v0.6.1
│   │   │   └── rsa v4.9.1
│   │   │       └── pyasn1 v0.6.1
│   │   ├── oauthlib v3.3.1
│   │   ├── python-dateutil v2.9.0.post0
│   │   │   └── six v1.17.0
│   │   ├── pyyaml v6.0.2
│   │   ├── requests v2.32.4 (*)
│   │   ├── requests-oauthlib v2.0.0
│   │   │   ├── oauthlib v3.3.1
│   │   │   └── requests v2.32.4 (*)
│   │   ├── six v1.17.0
│   │   ├── urllib3 v2.5.0
│   │   └── websocket-client v1.8.0
│   ├── mmh3 v5.1.0
│   ├── numpy v2.3.1
│   ├── onnxruntime v1.22.0 (*)
│   ├── opentelemetry-api v1.34.1
│   │   ├── importlib-metadata v8.7.0
│   │   │   └── zipp v3.23.0
│   │   └── typing-extensions v4.14.1
│   ├── opentelemetry-exporter-otlp-proto-grpc v1.34.1
│   │   ├── googleapis-common-protos v1.70.0
│   │   │   └── protobuf v5.29.5
│   │   ├── grpcio v1.73.1
│   │   ├── opentelemetry-api v1.34.1 (*)
│   │   ├── opentelemetry-exporter-otlp-proto-common v1.34.1
│   │   │   └── opentelemetry-proto v1.34.1
│   │   │       └── protobuf v5.29.5
│   │   ├── opentelemetry-proto v1.34.1 (*)
│   │   ├── opentelemetry-sdk v1.34.1
│   │   │   ├── opentelemetry-api v1.34.1 (*)
│   │   │   ├── opentelemetry-semantic-conventions v0.55b1
│   │   │   │   ├── opentelemetry-api v1.34.1 (*)
│   │   │   │   └── typing-extensions v4.14.1
│   │   │   └── typing-extensions v4.14.1
│   │   └── typing-extensions v4.14.1
│   ├── opentelemetry-sdk v1.34.1 (*)
│   ├── orjson v3.10.18
│   ├── overrides v7.7.0
│   ├── posthog v5.4.0
│   │   ├── backoff v2.2.1
│   │   ├── distro v1.9.0
│   │   ├── python-dateutil v2.9.0.post0 (*)
│   │   ├── requests v2.32.4 (*)
│   │   └── six v1.17.0
│   ├── pybase64 v1.4.1
│   ├── pydantic v2.11.7 (*)
│   ├── pypika v0.48.9
│   ├── pyyaml v6.0.2
│   ├── rich v14.0.0
│   │   ├── markdown-it-py v3.0.0
│   │   │   └── mdurl v0.1.2
│   │   └── pygments v2.19.2
│   ├── tenacity v9.1.2
│   ├── tokenizers v0.21.2 (*)
│   ├── tqdm v4.67.1
│   ├── typer v0.16.0
│   │   ├── click v8.2.1
│   │   ├── rich v14.0.0 (*)
│   │   ├── shellingham v1.5.4
│   │   └── typing-extensions v4.14.1
│   ├── typing-extensions v4.14.1
│   └── uvicorn v0.35.0
│       ├── click v8.2.1
│       └── h11 v0.16.0
├── langchain-core v0.3.72
│   ├── jsonpatch v1.33
│   │   └── jsonpointer v3.0.0
│   ├── langsmith v0.4.4
│   │   ├── httpx v0.28.1 (*)
│   │   ├── orjson v3.10.18
│   │   ├── packaging v24.2
│   │   ├── pydantic v2.11.7 (*)
│   │   ├── requests v2.32.4 (*)
│   │   ├── requests-toolbelt v1.0.0
│   │   │   └── requests v2.32.4 (*)
│   │   └── zstandard v0.23.0
│   ├── packaging v24.2
│   ├── pydantic v2.11.7 (*)
│   ├── pyyaml v6.0.2
│   ├── tenacity v9.1.2
│   └── typing-extensions v4.14.1
└── numpy v2.3.1
langchain-community v0.3.27
├── aiohttp v3.12.13
│   ├── aiohappyeyeballs v2.6.1
│   ├── aiosignal v1.4.0
│   │   └── frozenlist v1.7.0
│   ├── attrs v25.3.0
│   ├── frozenlist v1.7.0
│   ├── multidict v6.6.3
│   ├── propcache v0.3.2
│   └── yarl v1.20.1
│       ├── idna v3.10
│       ├── multidict v6.6.3
│       └── propcache v0.3.2
├── dataclasses-json v0.6.7
│   ├── marshmallow v3.26.1
│   │   └── packaging v24.2
│   └── typing-inspect v0.9.0
│       ├── mypy-extensions v1.1.0
│       └── typing-extensions v4.14.1
├── httpx-sse v0.4.1
├── langchain v0.3.26
│   ├── langchain-core v0.3.72 (*)
│   ├── langchain-text-splitters v0.3.8
│   │   └── langchain-core v0.3.72 (*)
│   ├── langsmith v0.4.4 (*)
│   ├── pydantic v2.11.7 (*)
│   ├── pyyaml v6.0.2
│   ├── requests v2.32.4 (*)
│   └── sqlalchemy v2.0.41 (*)
├── langchain-core v0.3.72 (*)
├── langsmith v0.4.4 (*)
├── numpy v2.3.1
├── pydantic-settings v2.10.1
│   ├── pydantic v2.11.7 (*)
│   ├── python-dotenv v1.1.1
│   └── typing-inspection v0.4.1 (*)
├── pyyaml v6.0.2
├── requests v2.32.4 (*)
├── sqlalchemy v2.0.41 (*)
└── tenacity v9.1.2
langchain-huggingface v0.3.1
├── huggingface-hub v0.34.3 (*)
├── langchain-core v0.3.72 (*)
└── tokenizers v0.21.2 (*)
langgraph v0.5.2
├── langchain-core v0.3.72 (*)
├── langgraph-checkpoint v2.1.0
│   ├── langchain-core v0.3.72 (*)
│   └── ormsgpack v1.10.0
├── langgraph-prebuilt v0.5.2
│   ├── langchain-core v0.3.72 (*)
│   └── langgraph-checkpoint v2.1.0 (*)
├── langgraph-sdk v0.1.72
│   ├── httpx v0.28.1 (*)
│   └── orjson v3.10.18
├── pydantic v2.11.7 (*)
└── xxhash v3.5.0
llama-cpp-python v0.3.12
├── diskcache v5.6.3
├── jinja2 v3.1.6
│   └── markupsafe v3.0.2
├── numpy v2.3.1
└── typing-extensions v4.14.1
mypy v1.16.1
├── mypy-extensions v1.1.0
├── pathspec v0.12.1
└── typing-extensions v4.14.1
passlib v1.7.4
psutil v7.0.0
pymupdf v1.26.3
pytest-cov v6.2.1
├── coverage v7.9.2
├── pluggy v1.6.0
└── pytest v8.4.1
    ├── iniconfig v2.1.0
    ├── packaging v24.2
    ├── pluggy v1.6.0
    └── pygments v2.19.2
pytest-mock v3.14.1
└── pytest v8.4.1 (*)
python-jose v3.5.0
├── ecdsa v0.19.1
│   └── six v1.17.0
├── pyasn1 v0.6.1
└── rsa v4.9.1 (*)
ruff v0.12.2
sentence-transformers v5.0.0
├── huggingface-hub v0.34.3 (*)
├── pillow v11.3.0
├── scikit-learn v1.7.0
│   ├── joblib v1.5.1
│   ├── numpy v2.3.1
│   ├── scipy v1.16.0
│   │   └── numpy v2.3.1
│   └── threadpoolctl v3.6.0
├── scipy v1.16.0 (*)
├── torch v2.7.1+cpu
│   ├── filelock v3.18.0
│   ├── fsspec v2025.5.1
│   ├── jinja2 v3.1.6 (*)
│   ├── networkx v3.5
│   ├── setuptools v80.9.0
│   ├── sympy v1.14.0 (*)
│   └── typing-extensions v4.14.1
├── tqdm v4.67.1
├── transformers v4.53.1
│   ├── filelock v3.18.0
│   ├── huggingface-hub v0.34.3 (*)
│   ├── numpy v2.3.1
│   ├── packaging v24.2
│   ├── pyyaml v6.0.2
│   ├── regex v2024.11.6
│   ├── requests v2.32.4 (*)
│   ├── safetensors v0.5.3
│   ├── tokenizers v0.21.2 (*)
│   └── tqdm v4.67.1
└── typing-extensions v4.14.1
slowapi v0.1.9
└── limits v5.4.0
    ├── deprecated v1.2.18
    │   └── wrapt v1.17.2
    ├── packaging v24.2
    └── typing-extensions v4.14.1
tavily-python v0.7.9
├── httpx v0.28.1 (*)
├── requests v2.32.4 (*)
└── tiktoken v0.9.0
    ├── regex v2024.11.6
    └── requests v2.32.4 (*)
tox-uv v1.26.1
├── packaging v24.2
├── tox v4.27.0
│   ├── cachetools v5.5.2
│   ├── chardet v5.2.0
│   ├── colorama v0.4.6
│   ├── filelock v3.18.0
│   ├── packaging v24.2
│   ├── platformdirs v4.3.8
│   ├── pluggy v1.6.0
│   ├── pyproject-api v1.9.0
│   │   └── packaging v24.2
│   └── virtualenv v20.31.2
│       ├── distlib v0.3.9
│       ├── filelock v3.18.0
│       └── platformdirs v4.3.8
└── uv v0.7.19
uvloop v0.21.0
watchfiles v1.1.0
└── anyio v4.9.0 (*)
websockets v15.0.1
(*) Package tree already displayed
  ```

</details>

---

## 3. Key Findings & Analysis

*This section documents the most significant findings from the analysis.*

-   **Finding 1: `torch` Dependency is Successfully Optimized.**
    -   **Analysis:** The tree confirms that `sentence-transformers` pulls in `torch vX.X.X+cpu`. The `+cpu` suffix is definitive proof that our configuration in `pyproject.toml` is working perfectly and we are installing the lean, CPU-only variant. This is a major success.

-   **Finding 2: `langchain-community` and `chromadb` are the Largest Sources of Transitive Dependencies.**
    -   **Analysis:** This is an expected and accepted trade-off. These libraries bring in a wide ecosystem of tools (`aiohttp`, `kubernetes`, `opentelemetry-api`, etc.) to provide their features. While we don't use all of these sub-dependencies directly, they are required for the libraries to function.

-   **Finding 3: `kubernetes` is an Unexpected but Accepted Dependency.**
    -   **Analysis:** The `kubernetes` client library is pulled in as a dependency of `chromadb`. ChromaDB includes this to support deployments on Kubernetes. This dependency is not removable without forking the library and is accepted as part of using ChromaDB.

---

## 4. Actionable Recommendations

-   **Recommendation 1: No Immediate Changes Required.**
    -   **Justification:** The dependency tree is clean and does not contain any unnecessary or critically bloated packages that can be easily removed. The optimizations we have already performed have addressed the most significant issues.
    -   **Action:** Formally accept the current dependency graph as the baseline for the project.

-   **Recommendation 2: Consider `langchain-core` for a Future "Run" Phase Optimization.**
    -   **Justification:** For an ultra-lean production build, a major refactoring to use only `langchain-core` and manually re-implementing needed functionality from `langchain-community` could significantly reduce the dependency footprint. This is a very large engineering effort.
    -   **Action:** Create a new, low-priority **`research` issue** in the Post-MVP backlog to track this long-term idea.
