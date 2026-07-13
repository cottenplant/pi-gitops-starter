# Bootstrap

From zero to "Flux is reconciling this skeleton". **Node provisioning is deliberately out of scope** — bring any
conformant cluster and this kit starts where `kubectl` works. The source cluster is k3s on Raspberry Pis; kind or k3d on
a laptop is fine for a dry run.

These commands mirror a live cluster's bootstrap; the demo path in this repo has not itself been cluster-tested end to
end.

## Prerequisites

- A Kubernetes cluster and a `kubectl` context pointed at it
- The `flux` CLI
- A GitLab project holding your copy of the `flux/` layout, and a PAT exported as `GITLAB_TOKEN`

## Steps

1. Bootstrap Flux with the image automation controllers — they are **not** part of the default component set — and a
   read-write deploy key, which the ImageUpdateAutomation needs to push tag pins back to the repo:

   ```sh
   flux bootstrap gitlab \
     --owner=<group> --repository=<flux-repo> --branch=main \
     --path=flux/clusters/demo \
     --components-extra=image-reflector-controller,image-automation-controller \
     --read-write-key
   ```

2. Flux commits its own components under `flux/clusters/demo/flux-system/` and starts reconciling everything else in
   that directory: `apps.yaml`, `images.yaml`, and `image-update-automation.yaml`.
3. Verify with `flux get kustomizations` — `apps-example-app` turns Ready once the Deployment points at an image you can
   actually pull (swap in a public placeholder image for a dry run, or wire up the
   [pull secret](../flux/components/pull-secret/README.md) for your registry).
4. Private registry? Follow the pull-secret README end to end — it covers the sops/age setup, the pull secret itself,
   and the separate scanning credential for the ImageRepository.

## What's still missing at skeleton stage

Nothing — the remaining hardening (alerting, backups, ingress) is your cluster's story, not this kit's.
