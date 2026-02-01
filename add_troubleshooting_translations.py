#!/usr/bin/env python3
"""
Add troubleshooting translations to all language files.
"""

import json
import os

# Translation data for all languages
translations = {
    "en": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "Step {number}",
                "estimatedTime": "{minutes} min",
                "successRate": "{rate}% success rate",
                "awaitingFeedback": "Please try this step and provide feedback",
                "workflowComplete": "✓ Problem resolved! The troubleshooting workflow is complete.",
                "workflowEscalated": "⚠ This issue requires expert assistance. Please use the escalation button to contact support.",
                "safetyWarning": "Safety Warning"
            },
            "feedback": {
                "worked": "It worked!",
                "partiallyWorked": "Partially worked",
                "didntWork": "Didn't work",
                "provideFeedback": "How did this step go?"
            },
            "errors": {
                "feedbackError": "Failed to submit feedback. Please try again."
            }
        }
    },
    "el": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "Βήμα {number}",
                "estimatedTime": "{minutes} λεπτά",
                "successRate": "{rate}% ποσοστό επιτυχίας",
                "awaitingFeedback": "Παρακαλώ δοκιμάστε αυτό το βήμα και δώστε ανατροφοδότηση",
                "workflowComplete": "✓ Το πρόβλημα επιλύθηκε! Η διαδικασία αντιμετώπισης προβλημάτων ολοκληρώθηκε.",
                "workflowEscalated": "⚠ Αυτό το ζήτημα απαιτεί βοήθεια ειδικού. Χρησιμοποιήστε το κουμπί κλιμάκωσης για επικοινωνία με την υποστήριξη.",
                "safetyWarning": "Προειδοποίηση Ασφαλείας"
            },
            "feedback": {
                "worked": "Λειτούργησε!",
                "partiallyWorked": "Λειτούργησε μερικώς",
                "didntWork": "Δεν λειτούργησε",
                "provideFeedback": "Πώς πήγε αυτό το βήμα;"
            },
            "errors": {
                "feedbackError": "Αποτυχία υποβολής ανατροφοδότησης. Παρακαλώ δοκιμάστε ξανά."
            }
        }
    },
    "ar": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "الخطوة {number}",
                "estimatedTime": "{minutes} دقيقة",
                "successRate": "{rate}% معدل النجاح",
                "awaitingFeedback": "يرجى تجربة هذه الخطوة وتقديم الملاحظات",
                "workflowComplete": "✓ تم حل المشكلة! اكتملت عملية استكشاف الأخطاء وإصلاحها.",
                "workflowEscalated": "⚠ تتطلب هذه المشكلة مساعدة خبير. يرجى استخدام زر التصعيد للاتصال بالدعم.",
                "safetyWarning": "تحذير السلامة"
            },
            "feedback": {
                "worked": "نجح الأمر!",
                "partiallyWorked": "نجح جزئياً",
                "didntWork": "لم ينجح",
                "provideFeedback": "كيف سارت هذه الخطوة؟"
            },
            "errors": {
                "feedbackError": "فشل إرسال الملاحظات. يرجى المحاولة مرة أخرى."
            }
        }
    },
    "es": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "Paso {number}",
                "estimatedTime": "{minutes} min",
                "successRate": "{rate}% tasa de éxito",
                "awaitingFeedback": "Por favor intente este paso y proporcione comentarios",
                "workflowComplete": "✓ ¡Problema resuelto! El flujo de solución de problemas está completo.",
                "workflowEscalated": "⚠ Este problema requiere asistencia experta. Use el botón de escalación para contactar al soporte.",
                "safetyWarning": "Advertencia de Seguridad"
            },
            "feedback": {
                "worked": "¡Funcionó!",
                "partiallyWorked": "Funcionó parcialmente",
                "didntWork": "No funcionó",
                "provideFeedback": "¿Cómo fue este paso?"
            },
            "errors": {
                "feedbackError": "Error al enviar comentarios. Por favor intente de nuevo."
            }
        }
    },
    "tr": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "Adım {number}",
                "estimatedTime": "{minutes} dakika",
                "successRate": "{rate}% başarı oranı",
                "awaitingFeedback": "Lütfen bu adımı deneyin ve geri bildirim sağlayın",
                "workflowComplete": "✓ Sorun çözüldü! Sorun giderme iş akışı tamamlandı.",
                "workflowEscalated": "⚠ Bu sorun uzman yardımı gerektiriyor. Destek ile iletişime geçmek için yükseltme düğmesini kullanın.",
                "safetyWarning": "Güvenlik Uyarısı"
            },
            "feedback": {
                "worked": "İşe yaradı!",
                "partiallyWorked": "Kısmen işe yaradı",
                "didntWork": "İşe yaramadı",
                "provideFeedback": "Bu adım nasıl gitti?"
            },
            "errors": {
                "feedbackError": "Geri bildirim gönderilemedi. Lütfen tekrar deneyin."
            }
        }
    },
    "no": {
        "aiAssistant": {
            "troubleshooting": {
                "stepNumber": "Trinn {number}",
                "estimatedTime": "{minutes} min",
                "successRate": "{rate}% suksessrate",
                "awaitingFeedback": "Vennligst prøv dette trinnet og gi tilbakemelding",
                "workflowComplete": "✓ Problem løst! Feilsøkingsarbeidsflyten er fullført.",
                "workflowEscalated": "⚠ Dette problemet krever ekspertstøtte. Bruk eskaleringknappen for å kontakte support.",
                "safetyWarning": "Sikkerhetsadvarsel"
            },
            "feedback": {
                "worked": "Det fungerte!",
                "partiallyWorked": "Fungerte delvis",
                "didntWork": "Fungerte ikke",
                "provideFeedback": "Hvordan gikk dette trinnet?"
            },
            "errors": {
                "feedbackError": "Kunne ikke sende tilbakemelding. Vennligst prøv igjen."
            }
        }
    }
}

def deep_merge(base, update):
    """Deep merge two dictionaries."""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def add_translations():
    """Add troubleshooting translations to all language files."""
    locales_dir = "frontend/src/locales"
    
    for lang_code, trans_data in translations.items():
        file_path = os.path.join(locales_dir, f"{lang_code}.json")
        
        # Read existing translations
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {file_path} not found, skipping...")
            continue
        
        # Merge new translations
        updated = deep_merge(existing, trans_data)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Updated {file_path}")

if __name__ == "__main__":
    add_translations()
    print("\n✓ All troubleshooting translations added successfully!")
