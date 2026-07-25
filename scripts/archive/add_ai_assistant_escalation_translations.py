#!/usr/bin/env python3

import json
import os

def add_ai_assistant_escalation_translations():
    """Add missing AI Assistant escalation translation keys to all language files."""
    
    # Translation keys to add
    escalation_translations = {
        "en": {
            "aiAssistant": {
                "escalate": "Escalate to Expert",
                "escalateTooltip": "Get help from a technical expert",
                "escalationModal": {
                    "title": "Escalate to Expert Support",
                    "description": "Our AI assistant will create a support ticket and connect you with a technical expert.",
                    "reasonLabel": "Escalation Reason",
                    "priorityLabel": "Priority Level",
                    "notesLabel": "Additional Notes",
                    "notesPlaceholder": "Please describe your issue in detail...",
                    "submitButton": "Create Support Ticket",
                    "cancelButton": "Cancel",
                    "reasons": {
                        "user_request": "I need expert help",
                        "low_confidence": "AI is uncertain",
                        "steps_exceeded": "Too many troubleshooting steps",
                        "safety_concern": "Safety issue detected",
                        "expert_required": "Complex technical issue"
                    },
                    "priorities": {
                        "low": "Low",
                        "medium": "Medium", 
                        "high": "High",
                        "urgent": "Urgent"
                    }
                },
                "escalationSuccess": {
                    "title": "Support Ticket Created",
                    "message": "Your escalation has been processed successfully.",
                    "ticketNumber": "Ticket Number",
                    "expertContact": "Expert Contact Information",
                    "nextSteps": "Next Steps",
                    "contactExpert": "Contact the expert using the information provided above.",
                    "referenceTicket": "Reference your ticket number when contacting support."
                }
            }
        },
        "el": {
            "aiAssistant": {
                "escalate": "Κλιμάκωση σε Ειδικό",
                "escalateTooltip": "Λάβετε βοήθεια από τεχνικό ειδικό",
                "escalationModal": {
                    "title": "Κλιμάκωση σε Υποστήριξη Ειδικών",
                    "description": "Ο AI βοηθός μας θα δημιουργήσει ένα εισιτήριο υποστήριξης και θα σας συνδέσει με έναν τεχνικό ειδικό.",
                    "reasonLabel": "Λόγος Κλιμάκωσης",
                    "priorityLabel": "Επίπεδο Προτεραιότητας",
                    "notesLabel": "Επιπλέον Σημειώσεις",
                    "notesPlaceholder": "Παρακαλώ περιγράψτε το πρόβλημά σας λεπτομερώς...",
                    "submitButton": "Δημιουργία Εισιτηρίου Υποστήριξης",
                    "cancelButton": "Ακύρωση",
                    "reasons": {
                        "user_request": "Χρειάζομαι βοήθεια ειδικού",
                        "low_confidence": "Το AI είναι αβέβαιο",
                        "steps_exceeded": "Πάρα πολλά βήματα αντιμετώπισης προβλημάτων",
                        "safety_concern": "Ανιχνεύθηκε πρόβλημα ασφάλειας",
                        "expert_required": "Σύνθετο τεχνικό πρόβλημα"
                    },
                    "priorities": {
                        "low": "Χαμηλή",
                        "medium": "Μεσαία",
                        "high": "Υψηλή", 
                        "urgent": "Επείγουσα"
                    }
                },
                "escalationSuccess": {
                    "title": "Εισιτήριο Υποστήριξης Δημιουργήθηκε",
                    "message": "Η κλιμάκωσή σας έχει επεξεργαστεί επιτυχώς.",
                    "ticketNumber": "Αριθμός Εισιτηρίου",
                    "expertContact": "Στοιχεία Επικοινωνίας Ειδικού",
                    "nextSteps": "Επόμενα Βήματα",
                    "contactExpert": "Επικοινωνήστε με τον ειδικό χρησιμοποιώντας τις παραπάνω πληροφορίες.",
                    "referenceTicket": "Αναφέρετε τον αριθμό εισιτηρίου σας όταν επικοινωνείτε με την υποστήριξη."
                }
            }
        },
        "ar": {
            "aiAssistant": {
                "escalate": "تصعيد إلى خبير",
                "escalateTooltip": "احصل على مساعدة من خبير تقني",
                "escalationModal": {
                    "title": "تصعيد إلى دعم الخبراء",
                    "description": "سيقوم مساعد الذكي الاصطناعي بإنشاء تذكرة دعم وربطك بخبير تقني.",
                    "reasonLabel": "سبب التصعيد",
                    "priorityLabel": "مستوى الأولوية",
                    "notesLabel": "ملاحظات إضافية",
                    "notesPlaceholder": "يرجى وصف مشكلتك بالتفصيل...",
                    "submitButton": "إنشاء تذكرة دعم",
                    "cancelButton": "إلغاء",
                    "reasons": {
                        "user_request": "أحتاج مساعدة خبير",
                        "low_confidence": "الذكي الاصطناعي غير متأكد",
                        "steps_exceeded": "خطوات استكشاف الأخطاء كثيرة جداً",
                        "safety_concern": "تم اكتشاف مشكلة أمان",
                        "expert_required": "مشكلة تقنية معقدة"
                    },
                    "priorities": {
                        "low": "منخفضة",
                        "medium": "متوسطة",
                        "high": "عالية",
                        "urgent": "عاجلة"
                    }
                },
                "escalationSuccess": {
                    "title": "تم إنشاء تذكرة الدعم",
                    "message": "تم معالجة تصعيدك بنجاح.",
                    "ticketNumber": "رقم التذكرة",
                    "expertContact": "معلومات الاتصال بالخبير",
                    "nextSteps": "الخطوات التالية",
                    "contactExpert": "اتصل بالخبير باستخدام المعلومات المقدمة أعلاه.",
                    "referenceTicket": "اذكر رقم تذكرتك عند الاتصال بالدعم."
                }
            }
        },
        "es": {
            "aiAssistant": {
                "escalate": "Escalar a Experto",
                "escalateTooltip": "Obtener ayuda de un experto técnico",
                "escalationModal": {
                    "title": "Escalar a Soporte de Expertos",
                    "description": "Nuestro asistente de IA creará un ticket de soporte y te conectará con un experto técnico.",
                    "reasonLabel": "Razón de Escalación",
                    "priorityLabel": "Nivel de Prioridad",
                    "notesLabel": "Notas Adicionales",
                    "notesPlaceholder": "Por favor describe tu problema en detalle...",
                    "submitButton": "Crear Ticket de Soporte",
                    "cancelButton": "Cancelar",
                    "reasons": {
                        "user_request": "Necesito ayuda de un experto",
                        "low_confidence": "La IA no está segura",
                        "steps_exceeded": "Demasiados pasos de solución de problemas",
                        "safety_concern": "Problema de seguridad detectado",
                        "expert_required": "Problema técnico complejo"
                    },
                    "priorities": {
                        "low": "Baja",
                        "medium": "Media",
                        "high": "Alta",
                        "urgent": "Urgente"
                    }
                },
                "escalationSuccess": {
                    "title": "Ticket de Soporte Creado",
                    "message": "Tu escalación ha sido procesada exitosamente.",
                    "ticketNumber": "Número de Ticket",
                    "expertContact": "Información de Contacto del Experto",
                    "nextSteps": "Próximos Pasos",
                    "contactExpert": "Contacta al experto usando la información proporcionada arriba.",
                    "referenceTicket": "Referencia tu número de ticket al contactar soporte."
                }
            }
        },
        "tr": {
            "aiAssistant": {
                "escalate": "Uzmana Yönlendir",
                "escalateTooltip": "Teknik uzman yardımı alın",
                "escalationModal": {
                    "title": "Uzman Desteğine Yönlendirme",
                    "description": "AI asistanımız bir destek bileti oluşturacak ve sizi teknik uzmanla bağlayacak.",
                    "reasonLabel": "Yönlendirme Nedeni",
                    "priorityLabel": "Öncelik Seviyesi",
                    "notesLabel": "Ek Notlar",
                    "notesPlaceholder": "Lütfen sorununuzu detaylı olarak açıklayın...",
                    "submitButton": "Destek Bileti Oluştur",
                    "cancelButton": "İptal",
                    "reasons": {
                        "user_request": "Uzman yardımına ihtiyacım var",
                        "low_confidence": "AI emin değil",
                        "steps_exceeded": "Çok fazla sorun giderme adımı",
                        "safety_concern": "Güvenlik sorunu tespit edildi",
                        "expert_required": "Karmaşık teknik sorun"
                    },
                    "priorities": {
                        "low": "Düşük",
                        "medium": "Orta",
                        "high": "Yüksek",
                        "urgent": "Acil"
                    }
                },
                "escalationSuccess": {
                    "title": "Destek Bileti Oluşturuldu",
                    "message": "Yönlendirmeniz başarıyla işlendi.",
                    "ticketNumber": "Bilet Numarası",
                    "expertContact": "Uzman İletişim Bilgileri",
                    "nextSteps": "Sonraki Adımlar",
                    "contactExpert": "Yukarıda verilen bilgileri kullanarak uzmanla iletişime geçin.",
                    "referenceTicket": "Destekle iletişime geçerken bilet numaranızı belirtin."
                }
            }
        },
        "no": {
            "aiAssistant": {
                "escalate": "Eskaler til Ekspert",
                "escalateTooltip": "Få hjelp fra en teknisk ekspert",
                "escalationModal": {
                    "title": "Eskaler til Ekspertstøtte",
                    "description": "Vår AI-assistent vil opprette en støtteticket og koble deg til en teknisk ekspert.",
                    "reasonLabel": "Eskaleringsårsak",
                    "priorityLabel": "Prioritetsnivå",
                    "notesLabel": "Tilleggsnotater",
                    "notesPlaceholder": "Vennligst beskriv problemet ditt i detalj...",
                    "submitButton": "Opprett Støtteticket",
                    "cancelButton": "Avbryt",
                    "reasons": {
                        "user_request": "Jeg trenger eksperthjelp",
                        "low_confidence": "AI er usikker",
                        "steps_exceeded": "For mange feilsøkingstrinn",
                        "safety_concern": "Sikkerhetsproblem oppdaget",
                        "expert_required": "Komplekst teknisk problem"
                    },
                    "priorities": {
                        "low": "Lav",
                        "medium": "Middels",
                        "high": "Høy",
                        "urgent": "Haster"
                    }
                },
                "escalationSuccess": {
                    "title": "Støtteticket Opprettet",
                    "message": "Din eskalering har blitt behandlet vellykket.",
                    "ticketNumber": "Ticketnummer",
                    "expertContact": "Ekspert Kontaktinformasjon",
                    "nextSteps": "Neste Steg",
                    "contactExpert": "Kontakt eksperten ved å bruke informasjonen gitt ovenfor.",
                    "referenceTicket": "Referer til ticketnummeret ditt når du kontakter støtte."
                }
            }
        }
    }
    
    # Language files to update
    language_files = [
        'frontend/src/locales/en.json',
        'frontend/src/locales/el.json', 
        'frontend/src/locales/ar.json',
        'frontend/src/locales/es.json',
        'frontend/src/locales/tr.json',
        'frontend/src/locales/no.json'
    ]
    
    for file_path in language_files:
        if os.path.exists(file_path):
            # Extract language code from filename
            lang_code = os.path.basename(file_path).replace('.json', '')
            
            try:
                # Read existing translations
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                
                # Add AI Assistant escalation translations
                if lang_code in escalation_translations:
                    if 'aiAssistant' not in translations:
                        translations['aiAssistant'] = {}
                    
                    # Merge escalation translations
                    translations['aiAssistant'].update(escalation_translations[lang_code]['aiAssistant'])
                    
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(translations, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ Updated {file_path} with AI Assistant escalation translations")
                else:
                    print(f"⚠️  No translations defined for language: {lang_code}")
                    
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n🎯 AI Assistant escalation translations added to all language files!")
    print("The 'aiAssistant.escalate' translation key error should now be resolved.")

if __name__ == "__main__":
    add_ai_assistant_escalation_translations()