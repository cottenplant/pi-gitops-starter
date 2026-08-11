# pi-gitops-starter

A small, self-validating starter kit for running Python services on a Raspberry Pi Kubernetes cluster with GitLab CI and
Flux.

Extracted from [moby](https://moby-pi.net) — a live 6-node Pi homelab — but rebuilt from scratch for publication: every
file in this repo was written for this repo.

## The chain

One pattern, end to end:

```text
git push → GitLab CI → container registry → Flux image automation → cluster
```

Three pieces demonstrate it:

- **`template/`** — a [Copier](https://copier.readthedocs.io) template for a Python service that fits the chain:
  uv-managed, Python 3.13, multi-stage arm64 Dockerfile with no apt layer, pytest, and a `.gitlab-ci.yml` that builds
  and tags images the way Flux image automation expects.
- **`example/example-app/`** — the template rendered with default answers, committed. CI re-renders the template on
  every pipeline and fails if the committed example drifts.
- **`flux/`** — a minimal GitOps repo skeleton showing the per-app Kustomization pattern: each app owns its whole
  footprint (namespace, NetworkPolicies, workloads, image automation) behind its own Flux Kustomization with pruning
  enabled. See [flux/README.md](flux/README.md).

## Quickstart

Generate a new service:

```sh
uvx copier copy https://gitlab.com/moby-pi/pi-gitops-starter.git my-service
```

Answer the prompts, then wire the result into your Flux repo using `flux/apps/example-app/` as the model. Later, pull
template improvements into your generated project with `copier update`.

To stand up the cluster side from scratch, see [docs/bootstrap.md](docs/bootstrap.md) — it starts where `kubectl` works;
node and OS provisioning are deliberately out of scope.

## Why these patterns

- **Per-app Flux Kustomizations** keep blast radius small: reconcile, suspend, or prune one app without touching the
  rest. Deleting an app's directory deletes the app — nothing else.
- **App-owned namespaces and NetworkPolicies** mean the app directory is the single source of truth for everything the
  app needs, including its isolation.
- **GitLab-native CI → registry → image automation** is the underdocumented sibling of the GitHub/GHCR homelab pattern.
  This repo is the validated recipe.
- **No secrets, ever.** This repo contains no secret material, encrypted or otherwise. Secret management is pointed at,
  not shipped — see [flux/components/pull-secret/](flux/components/pull-secret/README.md).

## Status

Snapshot-versioned, not a product. This kit is extracted from a real cluster and updated when the source patterns change
— pin a tag if you depend on it. Issues and MRs are welcome but response time is homelab-grade. Working on the kit
itself: run `pre-commit install` once after cloning; the hooks mirror the CI checks. Canonical home is GitLab, where
those pipelines run; [github.com/cottenplant/pi-gitops-starter](https://github.com/cottenplant/pi-gitops-starter) is a
read-only mirror.

The cluster it comes from is written up at [moby-pi.net](https://moby-pi.net).

## License

[MIT](LICENSE)
