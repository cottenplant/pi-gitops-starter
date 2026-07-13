# example-app

A small service.

Generated from [pi-gitops-starter](https://gitlab.com/moby-pi/pi-gitops-starter); pull template updates with
`copier update`.

## Develop

```sh
uv sync
uv run pytest
```

## Deploy

Pushing to the default branch builds an image via GitLab CI into `registry.gitlab.com/your-group/example-app`; Flux
image automation rolls it out. See the starter kit's `flux/` skeleton for the cluster side.
