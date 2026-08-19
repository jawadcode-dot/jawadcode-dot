# One-time setup: push README.md + assets/ + scripts/ to your GitHub profile repo.
#
# BEFORE RUNNING:
# 1. On github.com, create a new PUBLIC repo named EXACTLY your username, e.g. "jawadintech"
#    (Profile READMEs only work if repo name == username). Leave it empty, no README.
# 2. Replace YOUR_USERNAME below with your real GitHub username.
# 3. Run this script from this folder: powershell -ExecutionPolicy Bypass -File push-to-github.ps1

$username = "YOUR_USERNAME"
$remoteUrl = "https://github.com/$username/$username.git"

git init
git add README.md assets scripts
git commit -m "Add profile README with animated pixel avatar"
git branch -M main
git remote add origin $remoteUrl
git push -u origin main

Write-Host "Done. Visit https://github.com/$username to see it live."
