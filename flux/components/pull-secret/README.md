# pull-secret (pointer, not payload)

Pulling from a private GitLab registry needs an image pull secret in each app namespace. **This repo ships no secret
material, encrypted or otherwise** — even encrypted blobs disclose structure and key fingerprints.

Bring your own mechanism and wire it in as a Component here. Reasonable options:

- **SOPS + age** encrypted Secret manifests, decrypted by Flux's kustomize-controller (`spec.decryption`)
- **External Secrets Operator** against your secret store
- A GitLab **group deploy token** materialized per-namespace by whichever of the above you pick

TODO(v1): ship a SOPS-shaped example with a throwaway demo key, clearly marked as such.
