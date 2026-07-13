# Gotchas

Hard-won lessons from the source cluster, generalized. Each earned its place by burning a real afternoon.

## Pruning deletes Services too — and finalizers can wedge it

**Symptom:** an app's directory is deleted, Flux reports the prune done, but the namespace hangs in `Terminating`.
**Cause:** LoadBalancer Services carry load-balancer cleanup finalizers; if the LB controller never acks the deletion,
the finalizer never clears. **Fix:** check `kubectl get svc -A` for stuck finalizers before assuming a prune finished;
clear the orphaned finalizer only after confirming the LB resource is actually gone.

## Default-deny NetworkPolicy silently breaks DNS

**Symptom:** every connection from the pod fails, and every error message points at the app — timeouts, unknown host,
retry loops. **Cause:** a default-deny egress policy blocks port 53 to kube-dns like everything else; nothing resolves.
**Fix:** ship the DNS-egress allowance in the same component as the deny rule (see `flux/components/network-policies/`),
so no app can adopt one without the other.

## MR-built images can deploy before the MR merges

**Symptom:** an unreviewed change is live on the cluster. **Cause:** the ImagePolicy scans a registry path and picks the
highest timestamp — it has no concept of branches. An image built from an open MR lands in the same path and wins the
sort. **Fix:** build images from the default branch only, and never offer manual MR image builds. Review happens before
the build exists, not after.

## Flux ≥ 2.8 removed `.Updated` from commit templates

**Symptom:** image-automation commits stop after a Flux upgrade; the controller logs a template error. **Cause:** the
`messageTemplate` field `.Updated` was removed; `.Changed.Changes` is the replacement. **Fix:**
`{{range .Changed.Changes}}{{.NewValue}} {{end}}` — see `flux/clusters/demo/image-update-automation.yaml`.

## The namespace transformer rewrites flux-system objects

**Symptom:** image automation never fires; the ImagePolicy exists but in the wrong namespace. **Cause:** the app
kustomization sets `namespace: <app>`, and kustomize stamps it onto every resource it builds — including
ImageRepository/ImagePolicy objects that must live in `flux-system`. **Fix:** keep image CRs in a sibling `image/`
directory with its own kustomization (no `namespace:` field) and reconcile them via a separate Flux Kustomization.

## Validate manifests in CI, not on the cluster

**Symptom:** a typo'd manifest merges, and the first error you see is a failed reconciliation in production. **Cause:**
nothing between `git push` and kustomize-controller ever parsed the YAML. **Fix:**
`kustomize build | kubeconform -strict` in CI turns the same mistake into MR feedback (this repo's `kustomize-validate`
job is the working example).

## Slim CI images without git make tools degrade silently

**Symptom:** a job that resolves git state (copier, setuptools-scm, versioning plugins) "works" but produces subtly
wrong output. **Cause:** `-slim` images often ship without git, and many tools fall back to a degraded non-VCS mode
instead of failing. **Fix:** when a job needs repo metadata, use the non-slim image variant (this repo's `render-drift`
job hit exactly this).

## A merge to the flux repo IS a deploy

**Symptom:** "just merging config" restarts or breaks live workloads. **Cause:** Flux applies the default branch
continuously; there is no staging buffer between merge and cluster. **Fix:** treat flux-repo MRs with deploy-level care,
and prove structural changes are no-ops with a dry-run diff against the live cluster before merging.
