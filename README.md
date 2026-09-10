# student-ml-api

Production-style MLOps exercise: Flask prediction API with PR-gated CI, Docker, and GHCR releases.

**Repository:** https://github.com/AhyanAliKhan/student-ml-api  
**Package:** https://github.com/users/AhyanAliKhan/packages/container/package/student-ml-api

## Quick start (local)

```bash
python -m pip install -r requirements.txt
pytest -q
python app.py
# GET http://localhost:5000/health
```

## Docker

```bash
docker build -t student-ml-api:1.1.0 .
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:1.1.0
curl http://localhost:5000/health
```

## Pull from GHCR / rollback

```bash
docker pull ghcr.io/ahyanalikhan/student-ml-api:1.1.0
docker pull ghcr.io/ahyanalikhan/student-ml-api:1.0.0
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/ahyanalikhan/student-ml-api:1.0.0
```

## Workflow

`feature branch → Pull Request → CI (pytest + docker build check) → merge → git tag vX.Y.Z → Release → GHCR`

Evidence, digests, branch protection, and failure analysis: [docs/EVIDENCE.md](docs/EVIDENCE.md)
