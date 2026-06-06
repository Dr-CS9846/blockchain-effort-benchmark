# One-time GitHub bootstrap (do this once)

Publishes this `06_measurement` folder as a public, reproducible repo under
`github.com/Dr-CS9846` and switches the heavy scraping/measurement onto GitHub
Actions. After this, results are produced and committed automatically — no local
tools required.

## Option A — from VS Code terminal (recommended, most reliable)
```bash
cd "D:\PhD\3. Thesis\5. Pipeline\06_measurement"

# 1. create the repo on GitHub (via the website, "New repository"):
#    name: blockchain-effort-benchmark   visibility: Public   (no README — we have one)

# 2. publish this folder to it
git init
git add .
git commit -m "Initial commit: reproducible size->effort measurement pipeline"
git branch -M main
git remote add origin https://github.com/Dr-CS9846/blockchain-effort-benchmark.git
git push -u origin main
```
On push, GitHub Actions (`measure.yml`) runs automatically. Open the repo's
**Actions** tab to watch it; results land back in the repo as `measurements.csv`
and `size_effort_results.json`, and as a downloadable artifact.

> No personal access token is needed for the workflow — it uses GitHub's built-in
> `GITHUB_TOKEN`. Your push in step 2 uses your normal GitHub login.

## Option B — let Claude drive your open Chrome session
Claude can create the empty repo on github.com using your logged-in browser, and
can resolve the 13 delivered-repo URLs from the live W3F application pages (which
contain the links the local stubs lack). You still run the one `git push` above,
or upload via the web UI.

## After bootstrap — the only recurring human task
Keep `projects_manifest.csv` growing and correct (`repo_url` + `commit_sha`/`cutoff_date`).
Every change you push re-triggers measurement. That is the whole maintenance loop.

## Tell the nightly routine the repo exists
Create `5. Pipeline/_routine/REPO.md` containing one line — the repo URL —
so the nightly routine knows to fetch and reconcile the published results:
```
https://github.com/Dr-CS9846/blockchain-effort-benchmark
```
