# pull-secret

Injects a `gitlab-registry` image pull secret into every consuming app's namespace, sops-encrypted at rest in git.
**This repo ships no secret material, encrypted or otherwise** — you create the encrypted file; `secret.example.yaml`
shows the shape.

## Wiring it up

1. Create a GitLab **deploy token** with `read_registry` scope (project or group level).

2. Generate an age key and register its public half in [`../../.sops.yaml`](../../.sops.yaml):

   ```sh
   age-keygen -o age.agekey   # keep this file OUT of git; note the printed public key
   ```

3. Create and encrypt the secret (the `.enc.yaml` name matches the sops creation rule):

   ```sh
   kubectl create secret docker-registry gitlab-registry \
     --docker-server=registry.gitlab.com \
     --docker-username=<deploy-token-username> \
     --docker-password=<deploy-token> \
     --dry-run=client -o yaml > secret.enc.yaml
   sops --encrypt --in-place secret.enc.yaml
   ```

   Only then commit it — the kustomization references `secret.enc.yaml`, so the component fails closed until the
   encrypted file exists.

4. Give the cluster the private half so kustomize-controller can decrypt:

   ```sh
   kubectl create secret generic sops-age -n flux-system --from-file=age.agekey
   ```

5. Enable the consumers:
   - app kustomization: uncomment `- ../../components/pull-secret` under `components:`
   - app deployment: uncomment the `imagePullSecrets` block
   - `clusters/demo/apps.yaml`: uncomment the `decryption` block on each app Kustomization that builds encrypted files
   - scanning a private registry too? Point the ImageRepository `secretRef` at a token secret in `flux-system` (that's a
     separate secret — the image-reflector-controller reads it, not the kubelet)
