# student-ml-api — MLOps Assignment Evidence

Professional CI workflow with Pull Requests, Docker, and GHCR.

## Branch protection (Part 7)

Configure on GitHub → Settings → Branches → Add rule for `main`:

| Setting | Value |
|---|---|
| Require a pull request before merging | Enabled |
| Require approvals | 0 (solo student) or 1 |
| Require status checks to pass before merging | Enabled |
| Status check required | `Tests and Docker Build Check` |
| Require branches to be up to date before merging | Enabled (recommended) |
| Do not allow bypassing the above settings | Enabled if available |
| Restrict who can push to matching branches | Enabled / block direct pushes |
| Allow force pushes | Disabled |
| Allow deletions | Disabled |

These settings enforce: feature branch → PR → CI green → merge. Direct pushes to `main` are blocked.

## Merge strategy (Part 8)

**Selected: Squash and Merge**

Justification: keeps `main` history linear and readable (one commit per feature PR), while preserving detailed commits on the feature branch until merge. Ideal for assignment/demo repositories.

## CI vs Release workflows (Part 22)

| | CI (`ci.yml`) | Release (`release.yml`) |
|---|---|---|
| Trigger | PR → `main` (+ feature pushes) | Semantic tags `v*.*.*` |
| Tests | Yes | Yes |
| Docker build | Validate only | Build + push |
| Publish | **Never** | GHCR (`version`, `latest`, short SHA) |

Publishing from every PR is undesirable because:
- Unreviewed / unmerged code would become deployable artifacts
- Registry clutter and tag pollution (`latest` would thrash)
- Security risk: secrets used more often; supply-chain attack surface grows
- Traceability breaks: artifacts would not map cleanly to approved `main` commits/tags

## Commit-SHA image tags (Part 24)

Benefit: immutable pointer from a running container to an exact git commit even if semantic tags move or `latest` changes. Useful for incident response and bisecting regressions.

## Docker layer cache (Part 25)

Prefer:
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
```
Changing only `app.py` reuses the dependency layer. Copying the full tree first invalidates `pip install` on every source change, slowing CI.

## Rollback rationale (Part 20)

Pulling `student-ml-api:1.0.0` from the registry restores a known-good runtime **without** rebuilding, reinstalling dependencies, or hoping local environments match. `git clone` + `pip install` + `python app.py` is slow, environment-dependent, and not bit-for-bit identical to what production previously ran.

## Failure analysis (Part 26)

### Failure 1 — Failed pytest (deliberate CI break)

| | |
|---|---|
| **Symptom** | PR CI red; `assert data["status"] == "wrong"` fails |
| **Root cause** | Intentionally incorrect assertion in health test |
| **Evidence** | GitHub Actions failed run on the PR (see Actions tab) |
| **Correction** | Restore `assert data["status"] == "healthy"`; commit `fix: correct health endpoint test` |

### Failure 2 — Application bound to 127.0.0.1

| | |
|---|---|
| **Symptom** | Container healthy internally but `curl localhost:5000` from host fails / connection refused from outside container |
| **Root cause** | Flask default `host=127.0.0.1` only listens on loopback inside the container network namespace |
| **Evidence** | `docker logs` shows server on 127.0.0.1; host curl fails while `docker exec ... curl` may succeed |
| **Correction** | Bind `0.0.0.0` (gunicorn `--bind 0.0.0.0:5000`) |

### Failure 3 — Wrong container port (optional demo)

| | |
|---|---|
| **Symptom** | `curl localhost:5000/health` fails though container is running |
| **Root cause** | Published host port does not map to container listen port (`-p 5000:8000` mismatch) |
| **Evidence** | `docker ps` PORTS column; `docker inspect` PortBindings |
| **Correction** | Use `-p 5000:5000` matching `EXPOSE 5000` / CMD bind |

## Traceability chain for 1.1.0 (Part 21)

```
PR:                 #2
Merge Commit:       cfec48ff3094a77125818bda5440b80653068820
Git Tag:            v1.1.0
Docker Image:       ghcr.io/ahyanalikhan/student-ml-api:1.1.0
Image Digest:       sha256:f5ff37e096ae040ab189abc1e0bb0b1b69be02fa2aeea2521ff64532817c3310
Commit-SHA tag:     ghcr.io/ahyanalikhan/student-ml-api:cfec48f
```

### Also recorded for 1.0.0

```
PR:                 #1
Merge Commit:       1a95b76c88cdac7096c57716996ea2e15afa8785
Git Tag:            v1.0.0
Docker Image:       ghcr.io/ahyanalikhan/student-ml-api:1.0.0
Image Digest:       sha256:5e67f2797400014ec100018237e02c155dc462c1994ea8e7a3692ae282553277
```

### CI evidence links

| Event | Result | Run |
|---|---|---|
| Deliberate pytest failure | FAILED | https://github.com/AhyanAliKhan/student-ml-api/actions/runs/34470891785 |
| Health test fix | SUCCESS | https://github.com/AhyanAliKhan/student-ml-api/actions/runs/34470989217 |
| Release v1.0.0 | SUCCESS | https://github.com/AhyanAliKhan/student-ml-api/actions/runs/34471228152 |
| Release v1.1.0 | SUCCESS | https://github.com/AhyanAliKhan/student-ml-api/actions/runs/34471578296 |

### Repository / PRs

- Repo: https://github.com/AhyanAliKhan/student-ml-api
- PR #1: https://github.com/AhyanAliKhan/student-ml-api/pull/1
- PR #2: https://github.com/AhyanAliKhan/student-ml-api/pull/2
- Package: `ghcr.io/ahyanalikhan/student-ml-api` tags `1.0.0`, `1.1.0`, `latest`, `cfec48f`

### Docker inspection (Part 11) — sample from local run

| Field | Value |
|---|---|
| Container ID | `ab65eb55157f…` (varies per run) |
| Image ID | `sha256:c97171c1283a…` (local build) / registry digests above |
| Exposed port | `5000/tcp` → host `5000` |
| Running command | `gunicorn --bind 0.0.0.0:5000 app:app` |
| Working directory | `/app` |

## Docker layer cache observations (Part 25)

| Change | `COPY requirements.txt` / `pip install` | `COPY app.py` |
|---|---|---|
| Only `app.py` modified | **CACHED** | Rebuilt |
| `requirements.txt` modified | **Rebuilt** (~12s pip) | Rebuilt |

This is why dependency install is ordered before copying application source.

## Local Docker inspection checklist (Part 11)

```bash
docker images
docker ps
docker logs student-ml-api
docker inspect student-ml-api
docker exec -it student-ml-api sh
```

Record: Container ID, Image ID, Exposed port, Running command, Working directory (`/app`).

## Registry verification (Part 16)

```bash
docker pull ghcr.io/ahyanalikhan/student-ml-api:1.0.0
docker pull ghcr.io/ahyanalikhan/student-ml-api:latest
docker images --digests
```
