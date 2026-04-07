import re
import importlib.util
import os

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

        # Hard rule: ako korisnik traži skillove, vrati listu postojećih Python skillova.
        skill_keywords = [
            "koristi skill", "koristi skillove", "prikaži skill", "koji su skillovi",
            "koje skillove", "use skills", "list skills", "skills"
        ]
        if any(k in low for k in skill_keywords):
            skills = self.list_python_skills()
            if not skills:
                return ("list_skills", "Nema dostupnih Python skillova.")
            return ("list_skills", "Dostupni Python skillovi: " + ", ".join(skills))

        # Hard rule: vrijeme ide direktno preko weather skilla (ako postoji lokacija)
        loc = self._extract_weather_location(text)
        if loc and "weather" in self.list_python_skills():
            result = self.execute_skill("weather", f'location="{loc}"')
            return ("weather", result)

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
