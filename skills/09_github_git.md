# 🐙 GitHub i Git — Kompletno Znanje

## OBAVEZNO: Za git zadatke generiši skripte i komande — ne samo objašnjavaj

## Git Osnove

### Konfiguracija
```bash
git config --global user.name "Ime Prezime"
git config --global user.email "email@example.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main
```

### Svakodnevne Komande
```bash
# Status
git status
git log --oneline --graph --all

# Stage i commit
git add .
git add -p              # interaktivno
git commit -m "feat: dodaj login stranicu"
git commit --amend      # izmijeni zadnji commit

# Branch
git branch             # lista
git branch feature/login  # novi branch
git checkout feature/login
git checkout -b feature/login  # kreiraj i prebaci

# Merge i Rebase
git merge feature/login
git rebase main
git rebase -i HEAD~3   # interaktivni rebase

# Remote
git remote add origin https://github.com/user/repo.git
git push origin main
git push -u origin feature/login
git pull origin main
git fetch origin

# Undo
git restore .          # poništi izmjene
git restore --staged . # unstage sve
git reset HEAD~1       # poništi zadnji commit (čuvaj izmjene)
git reset --hard HEAD~1 # poništi commit I izmjene
git revert abc1234     # sigurno poništi (novi commit)
```

## Commit Poruke — Conventional Commits
```bash
feat:     nova funkcionalnost
fix:      ispravka greške
docs:     dokumentacija
style:    formatiranje (bez promjene logike)
refactor: refaktorisanje
test:     testovi
chore:    održavanje (build, CI)
perf:     poboljšanje performansi

# Primjeri
git commit -m "feat: dodaj Supabase sinkronizaciju"
git commit -m "fix: ispravi streaming response grešku"
git commit -m "docs: ažuriraj README sa Supabase uputama"
```

## Branching Strategy

### Git Flow
```
main          → produkcija
develop       → razvoj
feature/*     → nove funkcije
hotfix/*      → hitni popravci
release/*     → priprema za objavu
```

### GitHub Flow (jednostavniji)
```
main          → uvijek deployano
feature/*     → svaka nova funkcija
Pull Request  → review + merge
```

## GitHub — Specifičnosti

### GitHub CLI (gh)
```bash
# Instalacija
brew install gh  # Mac
winget install GitHub.cli  # Windows

# Auth
gh auth login

# Repo operacije
gh repo create moj-projekt --public
gh repo clone korisnik/repo

# Pull Request
gh pr create --title "Dodaj login" --body "Opis promjena"
gh pr list
gh pr merge 42

# Issues
gh issue create --title "Bug: login ne radi" --label bug
gh issue list
gh issue close 15
```

### GitHub Actions — CI/CD
```yaml
# .github/workflows/deploy.yml
name: Deploy na Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest
      
      - name: Deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up
```

### GitHub Actions — Automatski testovi
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install pytest
      - run: pytest tests/ -v
```

### .gitignore — Template
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.env
venv/
.venv/
*.egg-info/
dist/

# Node
node_modules/
.next/
dist/
.env.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Build
build/
out/
```

## Git Workflow — Tipični zadaci

### Novi projekt
```bash
mkdir moj-projekt && cd moj-projekt
git init
echo "# Moj Projekt" > README.md
echo "venv/" > .gitignore
git add .
git commit -m "feat: inicijalni commit"
gh repo create moj-projekt --public --source=. --push
```

### Rješavanje merge konflikta
```bash
git fetch origin
git checkout feature/moja-grana
git rebase origin/main
# Rješi konflikte u fajlovima
git add .
git rebase --continue
git push --force-with-lease
```

### Pregled historije
```bash
git log --oneline --graph --all --decorate
git log -p --follow src/komponenta.jsx  # historija fajla
git blame src/agent.py                  # ko je pisao što
git diff main..feature/login            # razlika između grana
```

### Stash (privremeno sačuvaj)
```bash
git stash
git stash push -m "WIP: login forma"
git stash list
git stash pop
git stash apply stash@{2}
```

## GitHub Pages (besplatan hosting)
```bash
# Za statični HTML sajt
git checkout -b gh-pages
# Stavi index.html u root
git push origin gh-pages
# Sajt je na: username.github.io/repo
```

## Skripte za Automatizaciju
```python
# Pokretanje git komandi iz Pythona
import subprocess

def git_commit_push(poruka):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", poruka])
    subprocess.run(["git", "push"])
    print(f"✅ Commit i push: {poruka}")

def git_status():
    result = subprocess.run(["git", "status", "--short"], 
                           capture_output=True, text=True)
    return result.stdout
```
