# Gotchas

Hard-won lessons from the source cluster, generalized. Each earns its place by having burned a real afternoon.

<!-- SKELETON: candidate list — expand each to a short section (symptom → cause → fix) at v1. -->

- **Pruning deletes Services too.** LoadBalancer Services can wedge on load-balancer cleanup finalizers; a "finished"
  prune may leave a namespace stuck terminating. Check finalizers before assuming Flux is done.
- **Default-deny NetworkPolicy silently breaks DNS.** Nothing resolves, and every symptom points at the app. Ship the
  DNS-egress allowance as part of the same baseline component as the deny rule.
- **Numeric tag sorting beats semver for continuous deployment.** Per-commit deploys don't have semver; a pipeline
  number embedded in the tag gives ImagePolicy a monotonic sort key.
- **Validate manifests in CI, not on the cluster.** `kustomize build | kubeconform` turns a failed reconciliation
  into MR feedback. A Flux repo without CI validation debugs its mistakes in production.
- **arm64 is a first-class constraint, not a footnote.** Some packages have no arm64 wheels; apt-based image builds
  drag in the slowest layer. uv-based multi-stage builds with no apt layer keep Pi builds fast and reproducible.
- **A merge to the Flux repo IS a deploy.** There is no "just merging config" — treat Flux-repo MRs with deploy-level
  care, and prove no-drift with a dry-run/diff before merging anything structural.
