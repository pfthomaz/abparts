#!/usr/bin/env python3
"""Create Spanish translations"""

import json

# Spanish translations
spanish_translations = {
  "common": {
    "save": "Guardar",
    "cancel": "Cancelar",
    "delete": "Eliminar",
    "edit": "Editar",
    "add": "Añadir",
    "create": "Crear",
    "update": "Actualizar",
    "search": "Buscar",
    "filter": "Filtrar",
    "export": "Exportar",
    "import": "Importar",
    "loading": "Cargando...",
    "error": "Error",
    "success": "Éxito",
    "confirm": "Confirmar",
    "yes": "Sí",
    "no": "No",
    "close": "Cerrar",
    "back": "Atrás",
    "next": "Siguiente",
    "previous": "Anterior",
    "submit": "Enviar",
    "reset": "Restablecer",
    "clear": "Limpiar",
    "select": "Seleccionar",
    "all": "Todos",
    "none": "Ninguno",
    "active": "Activo",
    "inactive": "Inactivo",
    "status": "Estado",
    "actions": "Acciones",
    "details": "Detalles",
    "view": "Ver",
    "download": "Descargar",
    "upload": "Subir",
    "refresh": "Actualizar",
    "print": "Imprimir"
  },
  "navigation": {
    "dashboard": "Panel de Control",
    "dashboardDescription": "Resumen de métricas y estado del sistema",
    "organizations": "Organizaciones",
    "organizationsDescription": "Gestionar jerarquía y relaciones de organizaciones",
    "organizationManagement": "Gestión de Organización",
    "organizationManagementDescription": "Gestión mejorada de organización, proveedores y almacenes",
    "parts": "Piezas",
    "partsDescription": "Explorar y gestionar catálogo de piezas",
    "orders": "Pedidos",
    "ordersDescription": "Crear y rastrear pedidos de piezas",
    "stocktake": "Inventario",
    "stocktakeDescription": "Realizar ajustes e inventarios de stock",
    "stockAdjustments": "Ajustes de Stock",
    "stockAdjustmentsDescription": "Registrar y rastrear ajustes de inventario",
    "maintenanceProtocols": "Protocolos de Mantenimiento",
    "maintenanceProtocolsDescription": "Gestionar plantillas de protocolos de mantenimiento",
    "maintenance": "Mantenimiento",
    "maintenanceDescription": "Realizar y rastrear mantenimiento",
    "machines": "Máquinas",
    "machinesDescription": "Ver y gestionar máquinas AutoBoss",
    "users": "Usuarios",
    "usersDescription": "Gestionar usuarios y permisos",
    "warehouses": "Almacenes",
    "warehousesDescription": "Gestionar ubicaciones y configuraciones de almacenes",
    "transactions": "Transacciones",
    "transactionsDescription": "Ver y gestionar historial de transacciones",
    "configuration": "Configuración",
    "configurationDescription": "Panel de configuración administrativa",
    "inventory": "Inventario",
    "reports": "Informes",
    "settings": "Ajustes",
    "profile": "Perfil",
    "security": "Centro de Seguridad",
    "logout": "Cerrar Sesión",
    "dailyOperations": "Operaciones Diarias",
    "categories": {
      "core": "Principal",
      "inventory": "Inventario",
      "operations": "Operaciones",
      "administration": "Administración"
    }
  },
  "auth": {
    "login": "Iniciar Sesión",
    "logout": "Cerrar Sesión",
    "username": "Nombre de Usuario",
    "password": "Contraseña",
    "email": "Correo Electrónico",
    "forgotPassword": "Olvidé mi Contraseña",
    "rememberMe": "Recordarme",
    "signIn": "Iniciar Sesión",
    "signOut": "Cerrar Sesión",
    "signUp": "Registrarse",
    "signInToAccount": "Inicia Sesión en tu Cuenta",
    "createAccount": "Crear Cuenta",
    "alreadyHaveAccount": "¿Ya tienes una cuenta?",
    "dontHaveAccount": "¿No tienes una cuenta?"
  },
  "users": {
    "title": "Usuarios",
    "addUser": "Añadir Usuario",
    "editUser": "Editar Usuario",
    "deleteUser": "Eliminar Usuario",
    "userDetails": "Detalles del Usuario",
    "name": "Nombre",
    "role": "Rol",
    "organization": "Organización",
    "createdAt": "Creado el",
    "lastLogin": "Último Acceso"
  },
  "dashboard": {
    "welcomeBack": "Bienvenido de nuevo, {{name}}",
    "quickActions": "Acciones Rápidas",
    "systemStatus": "Estado del Sistema",
    "allSystemsOperational": "Todos los sistemas operativos",
    "activeUsers": "Usuarios Activos",
    "onlineNow": "En línea ahora",
    "lowStock": "Stock Bajo",
    "needsAttention": "Necesita atención",
    "allGood": "Todo bien",
    "outOfStock": "Sin Stock",
    "critical": "Crítico",
    "allStocked": "Todo en stock",
    "pendingOrders": "Pedidos Pendientes",
    "inProgress": "En progreso",
    "noPending": "Sin pendientes",
    "recentActivity": "Actividad Reciente",
    "last24h": "Últimas 24h",
    "warehouses": "Almacenes",
    "activeLocations": "Ubicaciones activas",
    "attentionRequired": "Atención Requerida",
    "criticalStockAlert": "Alerta de Stock Crítico",
    "lowStockWarning": "Advertencia de Stock Bajo",
    "pendingInvitations": "Invitaciones Pendientes",
    "pendingOrdersOverview": "Resumen de Pedidos Pendientes",
    "lowStockByOrganization": "Stock Bajo por Organización",
    "currentStatus": "Estado actual",
    "errorLoading": "Error al cargar el panel de control"
  },
  "validation": {
    "required": "Este campo es obligatorio",
    "invalidEmail": "Dirección de correo electrónico no válida",
    "minLength": "La longitud mínima es de {{min}} caracteres",
    "maxLength": "La longitud máxima es de {{max}} caracteres",
    "invalidFormat": "Formato no válido"
  },
  "errors": {
    "generic": "Ocurrió un error. Por favor, inténtalo de nuevo.",
    "networkError": "Error de red. Por favor, verifica tu conexión.",
    "unauthorized": "No estás autorizado para realizar esta acción.",
    "notFound": "Recurso no encontrado.",
    "serverError": "Error del servidor. Por favor, inténtalo de nuevo más tarde."
  },
  "dailyOperations": {
    "title": "¡Lavemos las Redes!",
    "subtitle": "Flujo de trabajo de operaciones diarias - Comienza y termina tu día correctamente",
    "selectMachine": "Selecciona tu Máquina",
    "selectMachinePlaceholder": "-- Selecciona una máquina --",
    "sessionStatus": "Estado de la Sesión",
    "notStarted": "No Iniciado",
    "inProgress": "En Progreso",
    "completed": "Completado",
    "startDay": "Iniciar Día",
    "endDay": "Finalizar Día",
    "noMachines": "No hay máquinas disponibles",
    "noProtocols": "No hay protocolos configurados"
  }
}

# Load English file as base
with open('frontend/src/locales/en.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# Update with Spanish translations
for key in spanish_translations:
    en_data[key] = spanish_translations[key]

# Write Spanish file
with open('frontend/src/locales/es.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

print("✅ Created Spanish translation file")
