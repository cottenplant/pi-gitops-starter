# Architecture

Everything in this kit exists to demonstrate one chain:

```text
developer ──git push──▶ GitLab
                          │
                          ├─ CI: uv sync → pytest → docker build (native arm64)
                          │        │
                          │        ▼
                          │   registry ── tag: <pipeline-iid>-<shortsha>
                          │        │
                          ▼        ▼
                   GitRepository  ImageRepository ──▶ ImagePolicy
                          │                              │
                          └──── Kustomizations ◀── ImageUpdateAutomation
                                     │              (commits tag pins back to git)
                                     ▼
                            k8s cluster (arm64 / Raspberry Pi)
```

## Why image automation instead of CI applying manifests

The obvious wiring — CI runs `kubectl apply` after the build — couples deploy credentials to the CI runner and leaves no
declarative record of what's running. Here the arrow points the other way: CI only pushes an image; the cluster pulls.
Flux's image-reflector notices the new tag, the ImageUpdateAutomation rewrites the marked `image:` line in the flux repo
and commits it. Consequences worth having:

- **Git stays the single source of truth.** What's deployed is always readable from the repo, including history.
- **CI holds no cluster credentials.** A compromised pipeline can push a bad image but cannot touch the cluster.
- **Rollback is `git revert`** of the pin commit — no imperative undo, no snowflake state.

## The tag convention

The build job tags images `$CI_PIPELINE_IID-$CI_COMMIT_SHORT_SHA`, e.g. `1842-a1b2c3d`. Per-commit continuous deployment
has no meaningful semver, so the ImagePolicy needs something else to order by: GitLab's project-scoped pipeline IID is
monotonic and unique, including when pipelines overlap. The sha suffix never participates in the sort — it's there so a
running pod can be traced to its commit. The policy's `filterTags` regex extracts the numeric prefix and picks the
highest:

```yaml
filterTags:
  pattern: "^(?P<ts>[0-9]+)-[0-9a-f]+$"
  extract: "$ts"
policy:
  numerical:
    order: asc
```

The flip side of "highest pipeline IID wins" is a hazard: any matching image that lands in the scanned registry path
deploys. That is why the build job runs on the default branch only — see
[gotchas](gotchas.md#mr-built-images-can-deploy-before-the-mr-merges).

## The per-app boundary

Each app gets its own Flux Kustomization (`apps-<name>`) with `prune: true` and `wait: true`, pointing at a directory
the app fully owns: namespace, NetworkPolicies (via the shared component), workloads. Deleting the directory deletes the
app and nothing else; a broken manifest fails one app's reconciliation, not the whole tree.

The one thing that does NOT live inside the app's Kustomization is its ImageRepository/ImagePolicy pair. Those are
flux-system objects, and the app kustomization's `namespace:` transformer would rewrite them — so they sit in a sibling
`image/` directory with their own kustomization and are reconciled by the separate `images` Kustomization. The app still
owns the files; the cluster scopes them correctly.

## arm64 realities

- **Build natively.** The build job runs on GitLab's hosted arm64 runner (`saas-linux-small-arm64`) — qemu cross-builds
  are several times slower and occasionally subtly wrong.
- **No apt layer.** The Dockerfile installs nothing with apt; uv resolves Python and dependencies as wheels. Image
  builds stay fast and reproducible on 4-8GB nodes.
- **Check wheels before adopting a dependency.** Most of the scientific stack ships arm64 wheels now, but not all of it
  does; a source build of a C extension on a Pi can turn a 2-minute build into a 40-minute one.
