# Flux repo skeleton — the per-app Kustomization pattern

Layout for a GitOps repo where **each app owns its whole footprint** — namespace, NetworkPolicies, workloads, image
automation — behind its own Flux Kustomization with pruning enabled.

## Why per-app Kustomizations

- **Blast radius.** Reconcile, suspend, or roll back one app without touching the rest. A broken manifest fails one
  `apps-<name>` Kustomization, not the whole apps tree.
- **Prune with confidence.** The app directory is the single source of truth: delete `flux/apps/<name>/` and Flux
  deletes the app — namespace, netpols, everything — and nothing else.
- **App-owned isolation.** The namespace and its NetworkPolicies live next to the workload they protect, applied as a
  kustomize Component so every app gets the same default-deny baseline.

## Layout

```text
flux/
├── .sops.yaml            # encryption rule for *.enc.yaml (bring your own age key)
├── clusters/demo/        # cluster entry point: apps-<name> + images + image-update-automation
│   └── flux-system/      # populated by `flux bootstrap`, committed by Flux itself
├── apps/<name>/          # everything the app owns (ns, netpol via component, workload)
│   └── image/            # the app's flux-system image CRs — own kustomization, no namespace field
├── images/               # aggregates every apps/*/image dir for the images Kustomization
└── components/           # kustomize Components shared across apps
    ├── network-policies/ # default-deny baseline + DNS egress
    └── pull-secret/      # sops walkthrough + example — no secret material in this repo
```

## Gotchas (the short version)

- **Pruning deletes Services too**, and LoadBalancer Services can wedge on cloud/LB cleanup finalizers — check for stuck
  finalizers before assuming prune finished.
- **Default-deny NetworkPolicy blocks DNS** unless you explicitly allow egress to kube-dns; nothing resolves, and the
  failure looks like an app bug.
- **Validate before Flux does.** `kustomize build | kubeconform` in CI catches schema errors as MR feedback instead of
  as a failed reconciliation on the cluster.

Longer versions with context: [docs/gotchas.md](../docs/gotchas.md).
