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
3. Replace every `your-group` registry placeholder before expecting the demo to become Ready. For a public-image dry
   run, set both the Deployment image and ImageRepository path to a repository that exists. For a private GitLab
   registry, follow the [pull-secret guide](../flux/components/pull-secret/README.md) for both kubelet pulls and tag
   scanning.
4. Verify each link in the chain independently:

   ```sh
   flux check
   flux get kustomizations
   flux get image repository -n flux-system
   flux get image policy -n flux-system
   flux get image update -n flux-system
   ```

   Both `images` and `apps-example-app` should become Ready, the ImageRepository should report tags, and the ImagePolicy
   should select the highest pipeline-IID tag. After pushing a default-branch commit to the app repo, confirm that the
   automation commits the new image pin to Git and that `flux get kustomizations` reports the resulting revision.

## Skeleton boundary

The example allows cluster traffic to its HTTP port, but it does not install an Ingress or expose the Service outside
the cluster. Ingress, TLS, alerting, backups, and production secret lifecycle are deliberately left to the surrounding
cluster. The skeleton is operational only after its registry placeholders and credentials are wired up.
