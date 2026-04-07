import re
import importlib.util
import os
import inspect
from pathlib import Path

class HermesOrchestrator:
    def __init__(self, skills_dir="skills"):
        # Postavljamo putanju do foldera gdje su skillovi
        self.skills_dir = skills_dir

    def execute_skill(self, skill_name, params_str):
        """
        Traži .py datoteku u skills folderu i pokreće funkciju run()
        """
        # Provjera postoji li folder
        if not os.path.exists(self.skills_dir):
            return f"❌ Error: Skills directory '{self.skills_dir}' not found."

        # Putanja do datoteke (npr. skills/weather.py)
        file_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        
        if not os.path.exists(file_path):
            return f"❌ Error: Skill '{skill_name}' (Python version) not found in {self.skills_dir}."

        try:
            # Dinamičko učitavanje .py datoteke
            spec = importlib.util.spec_from_file_location(skill_name, file_path)
            skill_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(skill_module)

            # Parsiranje parametara iz stringa: location='Zagreb' -> {'location': 'Zagreb'}
            params = {}
            param_matches = re.findall(r"(\w+)=['\"](.+?)['\"]", params_str)
            for key, val in param_matches:
                params[key] = val

            print(f"🚀 [Orchestrator] Executing skill: {skill_name} with params: {params}")
            
            # Poziv funkcije run() unutar skripte
            if hasattr(skill_module, 'run'):
                # Normalizacija čestih aliasa parametara
                if "query" not in params and "input" in params:
                    params["query"] = params["input"]
                if "query" not in params and "prompt" in params:
                    params["query"] = params["prompt"]

                sig = inspect.signature(skill_module.run)
                required = [
                    name for name, p in sig.parameters.items()
                    if p.default is inspect._empty and p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
                ]

                # Ako postoji samo jedan obavezan parametar, a korisnik nije dao key=value,
                # tretiraj cijeli params_str kao vrijednost tog parametra.
                if not params and len(required) == 1 and params_str.strip():
                    raw = params_str.strip().strip("'\"")
                    params[required[0]] = raw

                result = skill_module.run(**params)
                return str(result)
            else:
                return f"❌ Error: Skill '{skill_name}' must have a 'run()' function."

        except Exception as e:
            return f"⚠️ Skill Execution Error: {str(e)}"

    def list_python_skills(self):
        if not os.path.exists(self.skills_dir):
            return []
        return sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(self.skills_dir)
            if f.endswith(".py")
        )

    def _actionable_skills(self):
        # Izbaci "numeričke" wrappere koji su više dokumentacija nego izvršni alati
        return [
            s for s in self.list_python_skills()
            if not re.match(r"^\d+_", s) and s not in {"skills_index"}
        ]

    def _infer_skill_from_context(self, text: str):
        low = (text or "").lower()
        actionable = self._actionable_skills()
        if not actionable:
            return None

        keyword_map = [
            ("weather", ["vrijeme", "weather", "temperatura", "kiša", "kisa", "vjetar"]),
            ("web_search", ["nađi", "nadji", "pretraži", "pretrazi", "search", "cijena", "koliko košta", "info", "najbolje"]),
            ("openclaw_skills", ["openclaw", "skill market", "market", "katalog skillova"]),
            ("hello", ["pozdrav", "hello", "bok", "cao"]),
        ]
        for skill, kws in keyword_map:
            if skill in actionable and any(k in low for k in kws):
                return skill

        return None

    def _skill_signature_hint(self, skill_name: str):
        file_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        if not os.path.exists(file_path):
            return None
        try:
            spec = importlib.util.spec_from_file_location(skill_name, file_path)
            skill_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(skill_module)
            if not hasattr(skill_module, "run"):
                return "run() funkcija nije pronađena."
            sig = inspect.signature(skill_module.run)
            return f"/skill {skill_name} {', '.join(str(p) for p in sig.parameters.values())}"
        except Exception:
            return None

    def _install_skill_pack(self, raw_name: str):
        wanted = (raw_name or "").strip().lower().replace("-", "_").replace(" ", "_")
        if not wanted:
            return "❌ Napiši ime skilla. Primjer: /install skill web_search"

        # 1) Ako već postoji Python skill, samo vrati uputu za poziv.
        if wanted in self.list_python_skills():
            hint = self._skill_signature_hint(wanted) or f"/skill {wanted} query=\"...\""
            return f"✅ Skill '{wanted}' je već dostupan.\nKoristi ga ovako: {hint}"

        # 2) Ako postoji SKILL.md pack istog imena.
        skill_pack = Path(self.skills_dir) / wanted / "SKILL.md"
        if skill_pack.exists():
            return f"✅ SKILL pack '{wanted}' je već instaliran na: {skill_pack}"

        # 3) Posebno mapiranje za upite poput 'znanje jezika' -> 08_znanje_jezika
        alias_map = {
            "znanje_jezika": "08_znanje_jezika",
            "web_pretrazivanje": "01_web_pretrazivanje",
        }
        mapped = alias_map.get(wanted)
        if mapped and mapped in self.list_python_skills():
            hint = self._skill_signature_hint(mapped) or f"/skill {mapped} query=\"...\""
            return f"✅ Skill '{mapped}' je dostupan.\nKoristi ga ovako: {hint}"

        return (
            f"❌ Skill '{raw_name}' nije pronađen.\n"
            "Instalacija packova: pokreni `bash scripts/install_skills.sh` u rootu projekta.\n"
            "Za listu dostupnih koristi: `Komande za skills`."
        )

    def _skills_help(self):
        return (
            "🧠 Komande za skills:\n"
            "- `/skills` ili `Komande za skills` → pomoć\n"
            "- `/skills list` → lista dostupnih Python skillova\n"
            "- `/skills read <ime>` → usage/info za skill\n"
            "- `/install skill <ime>` → provjera/instalacija skilla\n"
            "- `Use skill <ime>` → pokaži kako da pokreneš skill\n"
            "- `/skill <ime> param=\"vrijednost\"` → izvrši skill direktno"
        )

    def _read_skill_info(self, raw_name: str):
        wanted = (raw_name or "").strip().lower().replace("-", "_")
        if not wanted:
            return "❌ Napiši ime skilla. Primjer: /skills read web_search"
        if wanted in self.list_python_skills():
            hint = self._skill_signature_hint(wanted) or f"/skill {wanted} query=\"...\""
            return f"📘 Skill '{wanted}'\nPokretanje: {hint}"
        skill_pack = Path(self.skills_dir) / wanted / "SKILL.md"
        if skill_pack.exists():
            try:
                preview = skill_pack.read_text(encoding="utf-8")[:800]
                return f"📘 SKILL pack '{wanted}'\n{preview}"
            except Exception as e:
                return f"⚠️ Ne mogu pročitati '{wanted}': {e}"
        return f"❌ Skill '{raw_name}' nije pronađen."

    def _required_params_for_skill(self, skill_name: str):
        file_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        if not os.path.exists(file_path):
            return None
        try:
            spec = importlib.util.spec_from_file_location(skill_name, file_path)
            skill_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(skill_module)
            if not hasattr(skill_module, "run"):
                return None
            sig = inspect.signature(skill_module.run)
            return [
                name for name, p in sig.parameters.items()
                if p.default is inspect._empty and p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
            ]
        except Exception:
            return None

    def _extract_weather_location(self, text: str):
        # Primjeri: "kakvo je vrijeme u Splitu", "weather in Paris"
        m = re.search(r"(?:vrijeme|weather)\s+(?:u|za|in)\s+([A-Za-zČĆŽŠĐčćžšđ\-\s]+)\??", text, re.IGNORECASE)
        if not m:
            return None
        location = m.group(1).strip(" .,!?:;")
        return location if location else None

    def detect_intent_and_execute(self, user_text: str):
        text = (user_text or "").strip()
        low = text.lower()

        # Eksplicitna i prirodna komanda: /install skill <ime> | instaliraj skill <ime>
        m_install = re.search(r"(?:^|[\s,;:])(?:/?install|instaliraj|dodaj|ubaci)\s+skill\s+([a-zA-Z0-9_\-]+)", low, re.IGNORECASE)
        if m_install:
            requested = m_install.group(1).strip()
            return ("install_skill", self._install_skill_pack(requested))

        # Jednostavne slash komande: /skills, /skills list, /skills read <ime>, /skills help
        if low in {"/skills", "skills", "komande za skills", "komande skill", "/skills help"}:
            return ("skills_help", self._skills_help())
        m_skills_read = re.match(r"^/skills\s+read\s+(.+)$", low, re.IGNORECASE)
        if m_skills_read:
            return ("read_skill", self._read_skill_info(m_skills_read.group(1)))
        if low == "/skills list":
            skills = self.list_python_skills()
            if not skills:
                return ("list_skills", "Nema dostupnih Python skillova.")
            return ("list_skills", "Dostupni Python skillovi:\n- " + "\n- ".join(skills))

        # Eksplicitna komanda: "use skill <ime>" ili "skill <ime>" -> ne šalji na web_search
        m_use = re.match(r"^(?:use\s+skill|skill)\s+([a-zA-Z0-9_\-]+)$", low, re.IGNORECASE)
        if m_use:
            requested = m_use.group(1).strip().replace("-", "_")
            if requested in self.list_python_skills():
                hint = self._skill_signature_hint(requested) or f"/skill {requested} query=\"...\""
                return ("skill_help", f"✅ Skill '{requested}' je dostupan.\nPokreni ga ovako: {hint}")
            return ("skill_help", f"❌ Skill '{requested}' nije pronađen. Koristi 'Komande za skills' za listu.")

        # Eksplicitna komanda: /skill ime param="x"
        if low.startswith("/skill "):
            raw = text[len("/skill "):].strip()
            if not raw:
                return ("skill_error", "❌ Koristi format: /skill ime_skilla param=\"vrijednost\"")
            parts = raw.split(" ", 1)
            skill_name = parts[0].strip()
            params_str = parts[1].strip() if len(parts) > 1 else ""
            if not params_str:
                required = self._required_params_for_skill(skill_name)
                if required is None:
                    return ("skill_error", f"❌ Skill '{skill_name}' nije pronađen.")
                if required:
                    return ("skill_error", f"❌ Nedostaju parametri za skill '{skill_name}'. Primjer: /skill {skill_name} query=\"...\"")
                return (skill_name, self.execute_skill(skill_name, ""))
            return (skill_name, self.execute_skill(skill_name, params_str))

        # Hard rule: ako korisnik traži skillove, vrati listu postojećih Python skillova.
        skill_keywords = [
            "koristi skill", "koristi skillove", "prikaži skill", "koji su skillovi",
            "koje skillove", "use skills", "list skills", "skills"
        ]
        if any(k in low for k in skill_keywords):
            skills = self.list_python_skills()
            if not skills:
                return ("list_skills", "Nema dostupnih Python skillova.")
            return ("list_skills", "Dostupni Python skillovi:\n- " + "\n- ".join(skills) + "\n\nZa eksplicitan poziv koristi: /skill ime_skilla param=\"vrijednost\"")

        if "openclaw" in low and "openclaw_skills" in self.list_python_skills():
            return ("openclaw_skills", self.execute_skill("openclaw_skills", 'action="categories"'))

        if any(k in low for k in ["nađi", "nadji", "pretrazi", "pretraži", "search"]) and "web_search" in self.list_python_skills():
            return ("web_search", self.execute_skill("web_search", f'query="{text}"'))

        # Hard rule: vrijeme ide direktno preko weather skilla (ako postoji lokacija)
        loc = self._extract_weather_location(text)
        if loc and "weather" in self.list_python_skills():
            result = self.execute_skill("weather", f'location="{loc}"')
            return ("weather", result)

        # Kontekstualni auto-router: izaberi najkorisniji skill prema upitu
        inferred = self._infer_skill_from_context(text)
        if inferred == "web_search":
            return ("web_search", self.execute_skill("web_search", f'query="{text}"'))
        if inferred:
            return (inferred, self.execute_skill(inferred, text))

        return None

    def parse_response(self, ai_text):
        """
        Traži format [skill_name](params) u tekstu koji je AI generirao.
        """
        # Regex pattern za [ime-skilla](parametre)
        pattern = r"\[(.*?)\]\((.*?)\)"
        match = re.search(pattern, ai_text)

        if match:
            skill_name = match.group(1).strip()
            params_str = match.group(2).strip()
            return self.execute_skill(skill_name, params_str)
        
        return None
