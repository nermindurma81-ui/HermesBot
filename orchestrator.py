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
