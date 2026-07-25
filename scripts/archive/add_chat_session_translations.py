#!/usr/bin/env python3
"""
Add chat session management translations to all locale files.
"""

import json
import os

translations = {
    "en": {
        "newSession": "New Session",
        "confirmNewSession": "Start a new session? This will clear the current conversation.",
        "activeSession": "Active Session",
        "troubleshootingMode": "Troubleshooting Mode",
        "sessionCleared": "Session cleared. How can I help you today?"
    },
    "el": {
        "newSession": "Νέα Συνεδρία",
        "confirmNewSession": "Έναρξη νέας συνεδρίας; Αυτό θα διαγράψει την τρέχουσα συνομιλία.",
        "activeSession": "Ενεργή Συνεδρία",
        "troubleshootingMode": "Λειτουργία Αντιμετώπισης Προβλημάτων",
        "sessionCleared": "Η συνεδρία διαγράφηκε. Πώς μπορώ να σας βοηθήσω σήμερα;"
    },
    "ar": {
        "newSession": "جلسة جديدة",
        "confirmNewSession": "بدء جلسة جديدة؟ سيؤدي هذا إلى مسح المحادثة الحالية.",
        "activeSession": "جلسة نشطة",
        "troubleshootingMode": "وضع استكشاف الأخطاء",
        "sessionCleared": "تم مسح الجلسة. كيف يمكنني مساعدتك اليوم؟"
    },
    "es": {
        "newSession": "Nueva Sesión",
        "confirmNewSession": "¿Iniciar una nueva sesión? Esto borrará la conversación actual.",
        "activeSession": "Sesión Activa",
        "troubleshootingMode": "Modo de Solución de Problemas",
        "sessionCleared": "Sesión borrada. ¿Cómo puedo ayudarte hoy?"
    },
    "tr": {
        "newSession": "Yeni Oturum",
        "confirmNewSession": "Yeni oturum başlatılsın mı? Bu, mevcut konuşmayı temizleyecektir.",
        "activeSession": "Aktif Oturum",
        "troubleshootingMode": "Sorun Giderme Modu",
        "sessionCleared": "Oturum temizlendi. Bugün size nasıl yardımcı olabilirim?"
    },
    "no": {
        "newSession": "Ny Økt",
        "confirmNewSession": "Start en ny økt? Dette vil slette gjeldende samtale.",
        "activeSession": "Aktiv Økt",
        "troubleshootingMode": "Feilsøkingsmodus",
        "sessionCleared": "Økt slettet. Hvordan kan jeg hjelpe deg i dag?"
    }
}

def main():
    print("Adding chat session management translations...\n")
    
    for lang, trans in translations.items():
        file_path = f"frontend/src/locales/{lang}.json"
        
        if not os.path.exists(file_path):
            print(f"⚠️  {file_path} not found, skipping...")
            continue
        
        try:
            # Read existing translations
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure aiAssistant section exists
            if 'aiAssistant' not in data:
                data['aiAssistant'] = {}
            
            # Add new translations
            data['aiAssistant'].update(trans)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Updated {lang}.json with {len(trans)} translations")
            
        except Exception as e:
            print(f"❌ Error updating {lang}.json: {e}")
    
    print("\n✅ All translations added successfully!")
    print("\nNew translation keys added:")
    for key in translations["en"].keys():
        print(f"  - aiAssistant.{key}")

if __name__ == "__main__":
    main()
