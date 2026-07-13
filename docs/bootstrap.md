# Bootstrap

From zero to "Flux is reconciling this skeleton". **Node provisioning is deliberately out of scope** — bring any
conformant cluster and this kit starts where `kubectl` works. The source cluster is k3s on Raspberry Pis; kind or k3d
on a laptop is fine for a dry run.

<!-- SKELETON: commands are directional — validate the full path end-to-end at v1. -->

## Prerequisites

- A Kubernetes cluster and a `kubectl` context pointed at it
- The `flux` CLI
- A GitLab project holding your copy of the `flux/` layout, and a PAT exported as `GITLAB_TOKEN`

## Steps

1. Bootstrap Flux with the image automation controllers — they are **not** part of the default component set:

   ```sh
   flux bootstrap gitlab \
     --owner=<group> --repository=<flux-repo> --branch=main \
     --path=flux/clusters/demo \
     --components-extra=image-reflector-controller,image-automation-controller
   ```

2. Flux commits its own components under `flux/clusters/demo/flux-system/` and starts reconciling `apps.yaml`.
3. Verify with `flux get kustomizations` — `apps-example-app` turns Ready once the Deployment points at an image you
   can actually pull (swap in a public placeholder image for a dry run, or wire up the
   [pull secret](../flux/components/pull-secret/README.md) for your registry).

## What's still missing at skeleton stage

- TODO(v1): the `ImageUpdateAutomation` object and the write-access it needs to commit tag bumps back to git
- TODO(v1): pull-secret wiring for private registries
