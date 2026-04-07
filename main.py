import os
from orchestrator import HermesOrchestrator

# Inicijalizacija orchestratora
orchestrator = HermesOrchestrator()

def get_ai_response(user_input):
    """
    Ovdje ide tvoj poziv API-ju (OpenAI, Claude, itd.)
    Za sada koristimo simulaciju.
    """
    # SIMULACIJA: Ako korisnik kaže 'vrijeme', AI simulira poziv skilla
    if "vrijeme" in user_input.lower():
        return "[weather](location='Zagreb')"
    
    return "Ja sam HermesBot. Kako ti mogu pomoći?"

def main():
    print("🚀 HermesBot je pokrenut!")
    
    while True:
        user_input = input("Ti: ")
        if user_input.lower() in ["exit", "izlaz", "stop"]:
            break

        # 1. Dobij odgovor od AI-ja
        ai_reply = get_ai_response(user_input)

        # 2. Provjeri je li AI pozvao skill
        skill_result = orchestrator.parse_response(ai_reply)

        if skill_result:
            # Ako je skill pozvan, ispiši rezultat skilla
            print(f"🤖 HermesBot (Skill): {skill_result}")
        else:
            # Ako nije, samo ispiši običan odgovor
            print(f"🤖 HermesBot: {ai_reply}")

if __name__ == "__main__":
    main()
