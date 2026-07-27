# Pinned versions (must match the built image)

| App | Pin | Verified on this bench |
|-----|-----|------------------------|
| frappe | version-15 @ **v15.108.0** | 15.108.0 |
| erpnext | version-15 @ **v15.108.3** | 15.108.3 |
| my_store_ui | `full-feature-parity` @ `b3d1803c7703e868dbadbfe2ee2421d419e8588c` (tag `v1.0.0-rc2` / `v1.0.0-rc3`) | 0.0.1 |

**Do not use floating `main`/`develop` branches for a production image.** For a fully
reproducible build, replace the branch in `apps.json` with an exact tag or commit:

```json
{ "url": "https://github.com/frappe/frappe",  "branch": "v15.108.0" }
{ "url": "https://github.com/frappe/erpnext", "branch": "v15.108.3" }
{ "url": "https://github.com/YOUR-ORG/my_store_ui", "branch": "b3d1803c7703e868dbadbfe2ee2421d419e8588c" }
```

Base the image on the official `frappe/frappe_docker` custom-image build:
```
export APPS_JSON_BASE64=$(base64 -w0 deployment/apps.json)
docker build --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-15 \
  --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --tag=YOUR-REGISTRY/smj-erp:v1.0.0-rc3 \
  --file=images/custom/Containerfile .
```
(Run from a checkout of `frappe/frappe_docker`; push the immutable tag to your registry.)
