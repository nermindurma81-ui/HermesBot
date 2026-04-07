import re
import importlib.util
import os

class HermesOrchestrator:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir

    def execute_skill(self, skill_name, params_str):
        # Tražimo .py fajl u skills folderu
        file_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        
        if not os.path.exists(file_path):
            return f"❌ Skill '{skill_name}' ne postoji u folderu skills/ (provjeri imaš li .py fajl)"

        try:
            spec = importlib.util.spec_from_file_location(skill_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Pretpostavljamo da svaki skill ima funkciju run()
            # Parsiranje parametara (npr. location='Zagreb')
            params = {}
            param_matches = re.findall(r"(\w+)=['\"](.+?)['\"]", params_str)
            for key, val in param_matches:
                params[key] = val

            return module.run(**params)
        except Exception as e:
            return f"⚠️ Greška u skillu: {str(e)}"

    def parse_response(self, ai_text):
        # Traži [skill_name](params)
        match = re.search(r"\[(.*?)\]\((.*?)\)", ai_text)
        if match:
            return self.execute_skill(match.group(1), match.group(2))
        return None
