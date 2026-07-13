# Architecture

<!-- SKELETON: prose + diagram land at v1. This page explains the full chain once. -->

```text
developer ──git push──▶ GitLab
                          │
                          ├─ CI: uv sync → pytest → build image
                          │        │
                          │        ▼
                          │  registry (tag: <branch>-<shortsha>-<pipeline-iid>)
                          │        │
                          ▼        ▼
                    Flux GitRepository   Flux ImageRepository/ImagePolicy
                          │                    │
                          └──── Kustomization ◀┘  (image automation commits tag bumps back to git)
                                   │
                                   ▼
                              k8s cluster (arm64 / Raspberry Pi)
```

Sections to write at v1:

- Why image automation instead of CI running `kubectl apply` (git stays the source of truth; the cluster pulls)
- Tag convention and why the pipeline number is the sort key
- Where the per-app Kustomization boundary sits and what prune covers
- arm64 realities: wheel availability, no-apt images, build-arch choices
