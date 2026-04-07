# 🔍 Web Pretraživanje — Napredni Skill

## OBAVEZNO: Uvijek koristi web_search za aktuelne informacije

## Strategija pretraživanja

### Jednostavan upit
```
Korisnik: "šta je React 19?"
→ web_search("React 19 features 2024")
→ fetch_url(top_link)
→ Objasni na bosanskom
```

### Duboko istraživanje (3-5 pretrage)
```
1. web_search("[tema] overview")
2. web_search("[tema] tutorial examples")
3. web_search("[tema] best practices 2024")
4. fetch_url(najrelevantniji link)
5. write_file("istrazivanje_[tema].md", rezultati)
```

### Vijesti i aktuelnosti
```
web_search("[tema] news today")
web_search("[tema] latest update")
```

### Tehnička dokumentacija
```
web_search("[library] official docs")
fetch_url(docs_url) sa max_chars=8000
```

### Cijene i podaci
```
web_search("[proizvod] cijena 2024")
web_search("[kriptovaluta] price USD")
```

## Formulisanje upita — Savjeti
- Koristi engleski za tehničke upite (bolji rezultati)
- Dodaj godinu: "Python async 2024"
- Budi specifičan: "FastAPI file upload example" ne "kako uploadati fajl"
- Za probleme: "[error message] fix solution"
- Za poređenje: "[A] vs [B] comparison"

## Obavezni workflow
1. Pretraži → pročitaj rezultate
2. Fetch top 1-2 linka za detalje
3. Sačuvaj nalaze u fajl ako je složena tema
4. Prezentuj korisniku na bosanskom sa izvorima

## Kombinovanje sa drugim alatima
- web_search + fetch_url = kompletno istraživanje
- web_search + run_python = podaci + analiza
- web_search + create_webpage = istraživanje + vizualizacija
