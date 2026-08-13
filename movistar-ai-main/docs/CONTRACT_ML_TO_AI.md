# Contrato conceptual ML -> AI Engine

## 1. Propósito

Definir la información que el AI Engine necesita recibir del componente de Machine Learning para generar asistencia comercial sin recalcular ni modificar la recomendación.

## 2. Estado del contrato

- **Versión documental:** 0.1.
- **Estado:** borrador para alineación con el equipo de ML.
- **Autoridad sobre predicciones:** equipo de ML.
- **Consumidor:** AI Engine / Sales Copilot.
- **Implementación:** existe un adaptador local de referencia para 0.1; no existe integración real ni confirmación del equipo de ML.

Los nombres y tipos de este documento son conceptuales hasta que ambos equipos los confirmen.

## 3. Principios

- El payload representa una recomendación ya calculada.
- El AI Engine no cambia oferta, ranking ni probabilidades.
- Los campos predictivos ausentes no se inventan.
- Los identificadores deben permitir trazabilidad entre equipos.
- Una versión incompatible debe producir un error controlado.
- Los datos de cliente deben minimizarse y evitar PII innecesaria.

## 4. Campos obligatorios propuestos

Sin estos campos el AI Engine no puede generar una respuesta comercial normal.

| Campo | Tipo conceptual | Descripción | Regla |
|---|---|---|---|
| `request_id` | string | Correlación de la solicitud | No vacío y único para el intento |
| `recommendation_id` | string | Identificador estable de la recomendación | Debe conservarse en toda la conversación |
| `generated_at` | datetime ISO 8601 | Momento de generación | Debe incluir zona horaria o semántica acordada |
| `customer.customer_id` | string | Identificador anonimizado del cliente | No debe ser DNI ni teléfono |
| `primary_recommendation.offer_id` | string | Oferta recomendada por ML | Debe existir en la fuente de catálogo autorizada |
| `primary_recommendation.offer_name` | string | Nombre legible de la oferta | No sustituye la validación contra catálogo |
| `model_metadata.model_version` | string | Versión del modelo o paquete de modelos | Obligatoria para trazabilidad |

### Comportamiento ante ausencia

El AI Engine devuelve un error estructurado `ML_CONTRACT_INVALID` y no genera speech, rebate ni alternativa improvisada.

## 5. Campos opcionales propuestos

Su ausencia degrada capacidades específicas, pero no invalida necesariamente la recomendación.

| Campo | Tipo conceptual | Uso por AI Engine | Conducta si falta |
|---|---|---|---|
| `customer.profile_summary` | object | Personalizar tono y argumentos | Generar mensaje menos personalizado |
| `primary_recommendation.acceptance_probability` | number | Guidance interno y priorización visual | No mencionar probabilidad |
| `primary_recommendation.recommended_channel` | enum/string | Adaptar longitud y forma del speech | Usar canal informado por dashboard o estilo neutro |
| `primary_recommendation.recommended_moment` | object/string | Orientar contacto o seguimiento | No afirmar momento óptimo |
| `primary_recommendation.reason_codes` | array[string] | Explicación grounded y selección de argumentos | Usar solo hechos de catálogo y contexto disponible |
| `alternatives` | array[object] | Alternativas autorizadas ante objeción | No proponer otra oferta |
| `prediction_metadata` | object | Mostrar semántica o calidad si se acuerda | Omitir del guidance |
| `customer.language` | string | Elegir idioma | Usar idioma configurado para el MVP |
| `customer.preferred_channel` | string | Ajustar estilo | Usar canal de sesión o estilo neutro |
| `expires_at` | datetime | Evitar recomendaciones obsoletas | Aplicar política general de frescura pendiente |

Los campos opcionales nunca autorizan al AI Engine a recalcular resultados de ML.

## 6. Campos y decisiones pendientes de confirmar con ML

Estos elementos no forman todavía parte acordada del contrato.

| Tema o campo | Pregunta que debe resolver ML | Impacto |
|---|---|---|
| `contract_version` | ¿Qué estrategia de versionado compartirán los equipos? | Compatibilidad y despliegue |
| Coreografía | ¿ML invoca AI, dashboard reenvía el payload o AI consulta por ID? | Diseño de integración |
| `request_id` | ¿Quién lo crea y cuál es su alcance de unicidad? | Idempotencia |
| `recommendation_id` | ¿Es único globalmente y permanece estable? | Trazabilidad |
| `customer_id` | ¿Qué identificador anonimizado se usará? | Correlación y privacidad |
| Oferta | ¿ML envía solo `offer_id` o también snapshot de nombre/atributos? | Fuente de verdad y consistencia |
| Alternativas | ¿Se entregará top-k? ¿Todas son elegibles y están ordenadas? | Rebate y alternativas |
| Probabilidad | ¿Escala 0-1? ¿Está calibrada? ¿Condicionada a contacto? | Interpretación correcta |
| `reason_codes` | ¿Qué taxonomía, significado y cardinalidad tendrán? | Speech y explicabilidad |
| Canal | ¿Cuál es el enum compartido y qué significa una ausencia? | Adaptación de copy |
| Momento | ¿Será timestamp, ventana, etiqueta o no estará disponible? | Seguimiento |
| Frescura | ¿Cuánto tiempo es válida una recomendación? | Prevención de uso obsoleto |
| Zona horaria | ¿Qué zona y convención usarán los timestamps? | Orden y auditoría |
| Perfil resumido | ¿Lo entrega ML, dashboard u otra fuente? | Personalización |
| Campos sensibles | ¿Qué campos pueden mostrarse al asesor? | Privacidad |
| Sin recomendación | ¿Qué payload representa abstención o ausencia de candidatos? | Manejo de errores |
| Errores | ¿ML enviará códigos normalizados? | Degradación controlada |
| SLA | ¿Cuál es la latencia y disponibilidad esperada del intercambio? | Diseño del MVP |

## 7. Estructura ilustrativa

Este ejemplo no es todavía un schema ejecutable.

```json
{
  "contract_version": "0.1",
  "request_id": "req-123",
  "recommendation_id": "rec-456",
  "generated_at": "2026-08-11T10:30:00-05:00",
  "customer": {
    "customer_id": "CLI000001",
    "profile_summary": {
      "customer_type": "postpago",
      "age_range": "56-65",
      "tenure_months": 17,
      "has_mobile": true,
      "has_home": false,
      "app_user": true
    }
  },
  "primary_recommendation": {
    "offer_id": "OF004",
    "offer_name": "Plan Movil Ilimitado",
    "acceptance_probability": 0.71,
    "recommended_channel": "Call In",
    "recommended_moment": null,
    "reason_codes": [
      "HIGH_DATA_USAGE",
      "CURRENT_PLAN_NEAR_LIMIT"
    ]
  },
  "alternatives": [
    {
      "offer_id": "OF003",
      "offer_name": "Plan Movil Max 50GB",
      "acceptance_probability": 0.58,
      "reason_codes": ["HIGH_DATA_USAGE"]
    }
  ],
  "model_metadata": {
    "model_version": "nbo-v1"
  }
}
```

## 8. Validaciones del AI Engine

Al recibir el payload, el AI Engine debe verificar conceptualmente:

1. presencia de campos obligatorios;
2. sintaxis y versión soportada;
3. consistencia de IDs;
4. existencia de la oferta en el catálogo autorizado;
5. frescura, cuando se acuerde una política;
6. valores y enums dentro de dominios acordados;
7. ausencia o minimización de PII;
8. coherencia entre recomendación principal y alternativas;
9. que cualquier alternativa esté explícitamente autorizada.

## 9. Códigos de resultado esperados

| Código | Significado |
|---|---|
| `ML_CONTRACT_INVALID` | Falta o invalidez de un campo obligatorio |
| `ML_CONTRACT_UNSUPPORTED_VERSION` | Versión no soportada |
| `ML_RECOMMENDATION_NOT_FOUND` | No existe recomendación utilizable |
| `ML_RECOMMENDATION_EXPIRED` | Recomendación fuera de vigencia, si se acuerda expiración |
| `OFFER_CATALOG_MISMATCH` | Oferta no encontrada o inconsistente con catálogo |
| `ML_PAYLOAD_ACCEPTED` | Payload válido para construir contexto |

Los nombres definitivos también deben alinearse con dashboard.

## 10. Criterio de aceptación del contrato

El contrato podrá pasar de borrador a candidato aprobado cuando:

- ML confirme los campos obligatorios;
- exista acuerdo sobre IDs y versionado;
- se defina la coreografía de entrega;
- se aclare la semántica de probabilidades, reason codes, canal y momento;
- se defina el comportamiento sin recomendación;
- se acuerden ejemplos válidos e inválidos.
