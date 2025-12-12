#!/usr/bin/env python3

import json
import os

def add_daily_operations_translations():
    """Add Daily Operations page translation strings"""
    
    # Daily Operations translation strings
    translation_strings = {
        "dailyOperations": {
            "dayCompleted": "Day Completed!",
            "operationsInProgress": "Operations In Progress",
            "readyToStart": "Ready to Start",
            "allDailyChecksCompleted": "All daily checks completed for this machine today.",
            "startCompletedRememberEnd": "Start of day checks completed. Remember to complete end of day checks.",
            "beginDayWithStartChecks": "Begin your day by completing the start of day checks.",
            "startOfDay": "Start of Day",
            "preOperationChecks": "Pre-operation checks",
            "endOfDay": "End of Day",
            "postOperationChecks": "Post-operation checks",
            "beginStartOfDayChecks": "Begin Start of Day Checks",
            "noProtocolConfigured": "No protocol configured",
            "completed": "Completed",
            "completeEndOfDayChecks": "Complete End of Day Checks",
            "completeStartOfDayFirst": "Complete start of day checks first"
        }
    }

    # Language-specific translations
    language_translations = {
        "el": {
            "dailyOperations": {
                "dayCompleted": "Ημέρα Ολοκληρώθηκε!",
                "operationsInProgress": "Λειτουργίες σε Εξέλιξη",
                "readyToStart": "Έτοιμο για Έναρξη",
                "allDailyChecksCompleted": "Όλοι οι ημερήσιοι έλεγχοι ολοκληρώθηκαν για αυτό το μηχάνημα σήμερα.",
                "startCompletedRememberEnd": "Οι έλεγχοι έναρξης ημέρας ολοκληρώθηκαν. Θυμηθείτε να ολοκληρώσετε τους ελέγχους τέλους ημέρας.",
                "beginDayWithStartChecks": "Ξεκινήστε την ημέρα σας ολοκληρώνοντας τους ελέγχους έναρξης ημέρας.",
                "startOfDay": "Έναρξη Ημέρας",
                "preOperationChecks": "Έλεγχοι προ-λειτουργίας",
                "endOfDay": "Τέλος Ημέρας",
                "postOperationChecks": "Έλεγχοι μετά-λειτουργίας",
                "beginStartOfDayChecks": "Ξεκινήστε τους Ελέγχους Έναρξης Ημέρας",
                "noProtocolConfigured": "Δεν έχει ρυθμιστεί πρωτόκολλο",
                "completed": "Ολοκληρώθηκε",
                "completeEndOfDayChecks": "Ολοκληρώστε τους Ελέγχους Τέλους Ημέρας",
                "completeStartOfDayFirst": "Ολοκληρώστε πρώτα τους ελέγχους έναρξης ημέρας"
            }
        },
        "ar": {
            "dailyOperations": {
                "dayCompleted": "اكتمل اليوم!",
                "operationsInProgress": "العمليات قيد التقدم",
                "readyToStart": "جاهز للبدء",
                "allDailyChecksCompleted": "تم إكمال جميع الفحوصات اليومية لهذه الآلة اليوم.",
                "startCompletedRememberEnd": "تم إكمال فحوصات بداية اليوم. تذكر إكمال فحوصات نهاية اليوم.",
                "beginDayWithStartChecks": "ابدأ يومك بإكمال فحوصات بداية اليوم.",
                "startOfDay": "بداية اليوم",
                "preOperationChecks": "فحوصات ما قبل التشغيل",
                "endOfDay": "نهاية اليوم",
                "postOperationChecks": "فحوصات ما بعد التشغيل",
                "beginStartOfDayChecks": "ابدأ فحوصات بداية اليوم",
                "noProtocolConfigured": "لم يتم تكوين بروتوكول",
                "completed": "مكتمل",
                "completeEndOfDayChecks": "أكمل فحوصات نهاية اليوم",
                "completeStartOfDayFirst": "أكمل فحوصات بداية اليوم أولاً"
            }
        },
        "es": {
            "dailyOperations": {
                "dayCompleted": "¡Día Completado!",
                "operationsInProgress": "Operaciones en Progreso",
                "readyToStart": "Listo para Comenzar",
                "allDailyChecksCompleted": "Todas las verificaciones diarias completadas para esta máquina hoy.",
                "startCompletedRememberEnd": "Verificaciones de inicio de día completadas. Recuerda completar las verificaciones de fin de día.",
                "beginDayWithStartChecks": "Comienza tu día completando las verificaciones de inicio de día.",
                "startOfDay": "Inicio del Día",
                "preOperationChecks": "Verificaciones pre-operación",
                "endOfDay": "Fin del Día",
                "postOperationChecks": "Verificaciones post-operación",
                "beginStartOfDayChecks": "Comenzar Verificaciones de Inicio de Día",
                "noProtocolConfigured": "No hay protocolo configurado",
                "completed": "Completado",
                "completeEndOfDayChecks": "Completar Verificaciones de Fin de Día",
                "completeStartOfDayFirst": "Completa primero las verificaciones de inicio de día"
            }
        },
        "tr": {
            "dailyOperations": {
                "dayCompleted": "Gün Tamamlandı!",
                "operationsInProgress": "İşlemler Devam Ediyor",
                "readyToStart": "Başlamaya Hazır",
                "allDailyChecksCompleted": "Bu makine için bugünkü tüm günlük kontroller tamamlandı.",
                "startCompletedRememberEnd": "Gün başı kontrolleri tamamlandı. Gün sonu kontrollerini tamamlamayı unutmayın.",
                "beginDayWithStartChecks": "Gün başı kontrollerini tamamlayarak güne başlayın.",
                "startOfDay": "Gün Başı",
                "preOperationChecks": "Operasyon öncesi kontroller",
                "endOfDay": "Gün Sonu",
                "postOperationChecks": "Operasyon sonrası kontroller",
                "beginStartOfDayChecks": "Gün Başı Kontrollerini Başlat",
                "noProtocolConfigured": "Protokol yapılandırılmamış",
                "completed": "Tamamlandı",
                "completeEndOfDayChecks": "Gün Sonu Kontrollerini Tamamla",
                "completeStartOfDayFirst": "Önce gün başı kontrollerini tamamlayın"
            }
        },
        "no": {
            "dailyOperations": {
                "dayCompleted": "Dag Fullført!",
                "operationsInProgress": "Operasjoner Pågår",
                "readyToStart": "Klar til Start",
                "allDailyChecksCompleted": "Alle daglige sjekker fullført for denne maskinen i dag.",
                "startCompletedRememberEnd": "Start av dag sjekker fullført. Husk å fullføre slutt av dag sjekker.",
                "beginDayWithStartChecks": "Begynn dagen din ved å fullføre start av dag sjekker.",
                "startOfDay": "Start av Dag",
                "preOperationChecks": "Pre-operasjon sjekker",
                "endOfDay": "Slutt av Dag",
                "postOperationChecks": "Post-operasjon sjekker",
                "beginStartOfDayChecks": "Begynn Start av Dag Sjekker",
                "noProtocolConfigured": "Ingen protokoll konfigurert",
                "completed": "Fullført",
                "completeEndOfDayChecks": "Fullfør Slutt av Dag Sjekker",
                "completeStartOfDayFirst": "Fullfør start av dag sjekker først"
            }
        }
    }

    # Get the frontend locales directory
    locales_dir = "frontend/src/locales"
    
    if not os.path.exists(locales_dir):
        print(f"❌ Locales directory not found: {locales_dir}")
        return False

    success_count = 0
    
    # Process each language file
    for lang_code in ["en", "el", "ar", "es", "tr", "no"]:
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        
        try:
            # Load existing translations
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
            else:
                existing_translations = {}
            
            # Use language-specific translations if available, otherwise use English
            if lang_code in language_translations:
                new_strings = language_translations[lang_code]
            else:
                new_strings = translation_strings
            
            # Merge translations (deep merge for nested objects)
            for key, value in new_strings.items():
                if key in existing_translations and isinstance(existing_translations[key], dict) and isinstance(value, dict):
                    existing_translations[key].update(value)
                else:
                    existing_translations[key] = value
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_translations, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated {lang_code}.json with Daily Operations strings")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {lang_code}.json: {e}")
    
    print(f"\n🎉 Successfully updated {success_count}/6 language files with Daily Operations strings!")
    return success_count == 6

if __name__ == "__main__":
    add_daily_operations_translations()