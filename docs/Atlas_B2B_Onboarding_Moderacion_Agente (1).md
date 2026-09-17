# Atlas B2B — Onboarding, Moderación, Recomendación y Agente como Interfaz Administrativa

**Documento complementario** a la Propuesta de Solución Atlas B2B (fases 1/2/3). Este anexo desarrolla en detalle los puntos de retroalimentación recibidos tras la presentación inicial: cómo se incorporan negocios a la plataforma, cómo se controla el contenido que publican, cómo se enriquece la información para el sistema de recomendación y para el agente, y cómo el propio agente de WhatsApp actúa como interfaz administrativa para el negocio, no solo como canal de atención al cliente.

---

## 1. Alcance de este documento

Cubre seis áreas que se definieron como necesarias a partir de la retroalimentación:

1. Onboarding y verificación de negocios
2. Moderación de contenido (servicios, opciones, extras, perfil de negocio)
3. Etiquetado automático para el sistema de recomendación
4. Modelo de información por categoría (capa operativa vs. capa descriptiva)
5. Sistema de formularios personalizados (cliente, servicio, objetos repetibles)
6. El agente como interfaz administrativa dual sobre la misma API

Además incluye una revisión del modelo de pagos (simplificado respecto a la propuesta original) y una matriz de controles consolidada.

---

## 2. Entidades notables

| Entidad | Descripción |
|---|---|
| **Negocio (Organización)** | Cuenta que representa al negocio; agrupa empleados, servicios, perfil, y su estado de verificación. |
| **Empleado** | Usuario vinculado a un negocio y a un número de WhatsApp, con un rol (`administrador` / `operativo`). |
| **Categoría** | Clasificación cerrada del negocio (ej. "Consultorio médico", "Spa", "Taller mecánico"). Define plantillas de verificación y de perfil. |
| **Servicio** | Unidad reservable. Tiene capa operativa (precio, duración, capacidad, horario) y capa descriptiva (texto, FAQ). |
| **Opción / Extra** | Modificadores de precio sobre un servicio (opción: selección única; extra: selección múltiple). |
| **Etiqueta (Tag)** | Elemento de un catálogo cerrado usado por el sistema de recomendación (ej. "Clásico", "Romántico"). |
| **NegocioTag / ServicioTag / UsuarioTag** | Relación N a N entre negocio/servicio/usuario y una etiqueta, con peso de afinidad entre -1 y 1. |
| **Formulario** | Definición de campos personalizados asociada a un negocio (tipo cliente) o a un servicio (tipo servicio). |
| **Instancia de objeto repetible** | Registro concreto de un formulario de cliente marcado como repetible (ej. una mascota, un vehículo). |
| **Solicitud de contenido** | Evento de creación o edición sobre un negocio/servicio; pasa por el filtro de contenido y puede requerir revisión manual. |
| **Reserva** | Vincula cliente, servicio, opción/extras, respuestas de formulario, e instancia de objeto repetible (si aplica). |
| **Cliente** | Usuario final identificado por número de WhatsApp, con su propio perfil por negocio (formularios llenados, historial). |

---

## 3. Onboarding y verificación de negocios

### 3.1 Principio de diseño

Separar **"completar el perfil"** de **"verificar la identidad"**. Mezclarlos en un solo paso obligatorio genera abandono en negocios pequeños. Se permite operar y configurar rápido, pero se limitan las capacidades sensibles (sobre todo las relacionadas a mostrarse ante clientes reales) hasta completar la verificación.

### 3.2 Etapas

**Etapa 1 — Registro (self-service, rápido)**
- Datos de cuenta y empleados
- Nombre comercial, categoría/subcategoría
- Ubicación y horario general
- Estado resultante: `pendiente de verificación` — puede configurar servicios y probar el sistema, pero no aparece ante clientes reales.

**Etapa 2 — Verificación**
- Identidad legal: RNC (empresa) o cédula (persona física), validable contra el padrón público de la DGII
- Comprobante de dirección (si aplica local físico)
- Documentos adicionales requeridos por la **plantilla de la categoría** (ver sección 6) — ej. licencia/exequátur profesional para consultorios médicos y odontológicos
- Estado resultante: `verificado` — habilita visibilidad ante clientes y aprobación automática de reservas donde aplique

### 3.3 Revisión

Manual por el equipo interno al inicio (volumen bajo). La validación del RNC contra el padrón de la DGII puede automatizarse como consulta simple; la revisión de documentos/dirección permanece manual mientras el volumen lo justifique.

### 3.4 Manejo de disputas posteriores

- Reporte de cliente disponible vía el agente ("reportar un problema con esta reserva")
- Estado `suspendido`, aplicado manualmente por el equipo, que retira visibilidad sin borrar historial

### 3.5 Caso de uso — Alta de negocio

1. Usuario inicia registro, completa datos básicos y categoría → negocio queda `pendiente de verificación`.
2. Usuario configura servicios (visibles solo en su propio panel/agente, no públicos).
3. Usuario sube documentos de verificación (genéricos + los que exija su categoría).
4. Equipo revisa manualmente; valida RNC/cédula contra DGII.
5. **Aprobado:** negocio pasa a `verificado`, se habilita visibilidad pública y aprobación automática donde el servicio lo permita.
6. **Rechazado:** negocio recibe motivo y puede corregir y reenviar documentos.

### 3.6 Controles

- Gate de visibilidad pública atado al estado `verificado`
- Cuenta/contacto de pago ligado a identidad verificada (relevante para el modelo de pagos revisado, sección 9)
- Checklist de documentos dependiente de categoría, no fijo para todos los negocios

---

## 4. Moderación de contenido

### 4.1 Filtro de contenido (lista negra)

Pieza reutilizable aplicada a cualquier campo de texto libre: nombre/descripción de negocio, nombre/descripción de servicio, opciones, extras.

- Lista negra organizada por categorías: sustancias ilegales, contenido sexual/explícito, armas/violencia, lenguaje de fraude, discurso de odio.
- Normalización previa a la comparación: minúsculas, sin acentos, colapso de espaciado/repetición, sustituciones tipo leetspeak, coincidencia por límite de palabra.
- Mecanismo determinístico (no clasificador de IA): predecible, explicable, fácil de mantener por el equipo.

### 4.2 Flujo según entidad

**Negocio (perfil general):** ingreso siempre **manual**, revisado por el equipo como parte de la verificación (sección 3). El filtro corre como señal de apoyo al revisor (resalta qué campo disparó qué coincidencia), no reemplaza la revisión humana.

**Servicio, opción, extra:** ingreso **automático** por defecto — se publica de inmediato — salvo que el filtro detecte coincidencia:

1. Queda en estado `en revisión`: no visible ni reservable, visible en el panel del negocio con nota explicativa.
2. Notificación al negocio (vía agente) de que quedó pendiente.
3. Entra a cola de revisión manual, con la coincidencia específica resaltada.
4. Revisor **aprueba** (publica) o **rechaza** (queda oculto, con motivo; negocio puede editar y reenviar).

### 4.3 Solicitudes de edición — versión publicada + pendiente

Para que una edición nunca haga desaparecer un servicio ya publicado:

- El servicio mantiene una **versión publicada** (lo que ven clientes y agente) y, opcionalmente, **una solicitud de edición pendiente** (0 o 1 activa a la vez).
- Al editar, se crea una solicitud con el diff de campos. El filtro corre solo sobre los campos de texto libre que cambiaron (precio/horario/capacidad no pasan por el filtro).
  - **Sin coincidencia:** aprobación automática e inmediata; la solicitud reemplaza la versión publicada al instante.
  - **Con coincidencia:** la solicitud queda `en revisión`, entra a cola manual; la versión publicada **no se toca**.
- **Tratamiento atómico:** toda la solicitud se aprueba o queda pendiente como unidad (no por campo individual), para simplificar el modelo de estado.
- **Reemplazo de solicitud pendiente:** una nueva edición mientras hay una solicitud `en revisión` reemplaza a la anterior (última edición gana), reiniciando su evaluación.
- Creación y edición usan el mismo mecanismo (`solicitud de contenido`): la creación es una solicitud sin versión publicada previa.

### 4.4 Controles

- Trazabilidad: qué coincidió, quién decidió, para afinar la lista negra con el tiempo
- Señal de reincidencia: negocio con múltiples rechazos es candidato a revisión de cuenta completa, no solo del ítem puntual
- Notificación al negocio en ambos desenlaces (aprobado/rechazado), con motivo si fue rechazo

---

## 5. Etiquetado automático para el sistema de recomendación

### 5.1 Caso de uso

Al crear o editar un negocio/servicio, el sistema solicita al **agente de IA** (reutilizando la misma infraestructura conversacional de Atlas) que clasifique el texto (nombre + descripción) contra el catálogo cerrado de etiquetas, devolviendo qué etiquetas aplican y con qué peso. El agente nunca inventa etiquetas fuera del catálogo — la salida se restringe a la lista cerrada.

### 5.2 Características

- **No visible** para el negocio ni para el cliente final — es una tarea de enriquecimiento de datos en segundo plano, sin pantalla ni paso de confirmación.
- Corre en el mismo evento disparador que el filtro de contenido (creación o solicitud de edición), pero de forma **independiente y no bloqueante**: no depende de si el contenido pasó o no la moderación.
- Alimenta directamente la relación `NegocioTag` / `ServicioTag` (peso entre -1 y 1; en la práctica, fase 1 solo produce pesos positivos, ya que inferir afinidad negativa desde texto es más propenso a error).
- El catálogo de tags es cerrado y curado por el equipo — no crece con contenido de negocios individuales.
- `UsuarioTag` (afinidad de cliente) se alimenta de comportamiento/interacciones, no de este mecanismo — comparte el catálogo de tags pero es un proceso aparte.

---

## 6. Modelo de información por categoría

### 6.1 Dos capas separadas

- **Capa operativa:** precio, duración, capacidad, horario, política de pago. Estructura rígida porque afecta el cálculo del motor de reservas.
- **Capa descriptiva/comunicacional:** descripción, políticas, requisitos previos, FAQ, campos de categoría. Es lo que alimenta directamente el contexto conversacional del agente, y su formato varía según el propósito de cada pieza (ver 6.2).

### 6.2 Clasificación detallada de la capa descriptiva

No es un solo campo de texto — son piezas distintas, diferenciadas por **para qué las usa el agente**, **cuándo las trae a la conversación**, y **si tienen o no efecto funcional** sobre el sistema. Todas las define el negocio una vez (a diferencia de los formularios, que los llena el cliente — sección 7), y todas pasan por el filtro de contenido (sección 4).

| Tipo | Propósito | Momento de uso | Formato | Efecto funcional |
|---|---|---|---|---|
| **Descripción** | Presentar/vender — de qué se trata, qué experimenta el cliente | Exploración, recomendación ("cuéntame de X") | Texto libre corto, un bloque | No |
| **Políticas** | Condicionar cómo se presta el servicio una vez reservado (cancelación, tardanza, qué traer) | Al reservar/confirmar | Mixto: informativas en texto libre; las que implican ventana de tiempo (ej. cancelación) son candidatas a campo estructurado a futuro | No en fase 1 (solo comunicadas, no aplicadas) |
| **Requisitos previos** | Filtrar/advertir si el cliente puede reservar en absoluto (ej. mayoría de edad, prescripción previa, no apto para embarazadas) | Exploración/cotización, de forma **proactiva** — antes de avanzar todo el flujo | Lista corta de condiciones, un ítem por condición | No en fase 1 (candidato a validación real más adelante, ej. cruzar con edad del formulario de cliente) |
| **FAQ** | Resolver dudas puntuales y recurrentes que no ameritan estar en la descripción | Reactivo, ante pregunta específica del cliente | Lista de pares `{pregunta, respuesta}` — no un bloque, para que el agente matchee la pregunta del cliente contra la más parecida | No |
| **Campos de categoría** | Datos puntuales del rubro para filtrado/búsqueda (ej. seguros aceptados, tipo de cocina) | Reactivo, o como parte de una recomendación filtrada | Estructurado, tipo de dato conocido (definido por la plantilla de categoría) | No en fase 1, salvo uso en búsqueda/filtro |

**Distinción clave — Políticas vs. Requisitos previos:** las políticas condicionan *cómo* se presta el servicio ya reservado; los requisitos previos determinan *si* el cliente puede reservarlo en absoluto. Por eso conviene que el agente los use en momentos distintos: los requisitos previos se mencionan temprano (para no hacerle perder tiempo al cliente si no califica), las políticas se comunican al confirmar.

**Distinción clave — FAQ vs. Campos de categoría:** el FAQ es contenido redactado libremente por el negocio, pensado para preguntas específicas de ese negocio; los campos de categoría son datos estructurados y comparables entre negocios de la misma categoría, útiles también para que el sistema filtre/recomiende entre varios negocios, no solo para responder sobre uno en particular.

### 6.3 Esquema por categoría (no por negocio individual)

La variabilidad de "qué información pedir" no vive en cada negocio (eso llevaría a esquemas libres descontrolados), sino en la **categoría**, mantenida por el equipo:

1. **Documentos de verificación requeridos** — la mayoría de categorías solo requiere lo genérico (RNC/cédula); categorías reguladas (consultorio médico, odontología, etc.) requieren licencia/exequátur.
2. **Campos de perfil sugeridos** — preguntas específicas del rubro (ej. médico: especialidad, seguros aceptados; restaurante: tipo de cocina, opciones dietéticas), que alimentan la capa descriptiva.
3. **Badge de confianza category-aware** — para categorías reguladas, una vez validado el documento, el agente puede comunicarlo como señal de confianza ante el cliente.

### 6.4 Consumo por el agente

Dado el volumen esperado (negocios pequeños, perfiles compactos), el perfil completo (descripción + políticas + requisitos previos + FAQ + campos de categoría) se **inyecta directo como contexto** cuando el agente entra en conversación sobre ese negocio — no requiere búsqueda semántica/RAG en fase 1. Se revisaría solo si en el futuro los catálogos crecen mucho.

---

## 7. Sistema de formularios personalizados

### 7.1 Tipos de formulario

| Tipo | Se pide | Dónde vive la respuesta |
|---|---|---|
| **Formulario de cliente** | Una vez, al convertirse en cliente de ese negocio (o el negocio marca campos para repreguntar) | Perfil del cliente, por negocio |
| **Formulario de servicio** | En el momento de reservar ese servicio específico | Atado a la reserva |
| **Objeto repetible del cliente** | En cualquier momento; el cliente puede crear varias instancias | Instancias propias del cliente, por negocio |

### 7.2 Tipos de campo soportados (set cerrado, MVP)

Texto corto, texto largo, número, selección única, selección múltiple, sí/no, fecha. Cada campo con etiqueta, obligatoriedad y texto de ayuda opcional. Sin validación condicional entre campos en fase 1.

### 7.3 Objetos repetibles

Un formulario de cliente puede marcarse `permite múltiples instancias`, representando un tipo de objeto que el cliente puede tener varios (mascota, vehículo, propiedad):

- Requiere un campo identificador simple, usable por el agente en conversación ("Firulais", "Corolla 2020").
- El cliente puede crear instancias en cualquier momento, no solo al volverse cliente.
- Un servicio puede **vincularse a un tipo de objeto repetible**: al reservar, el agente resuelve primero la instancia (selección entre existentes o creación de una nueva) y luego continúa con los campos propios del servicio (si tiene).
- Vive a nivel de negocio, no global — las instancias no se comparten entre negocios distintos.
- Soporta edición y eliminación de instancias vía conversación con el agente.

### 7.4 Caso de uso — Reserva con objeto repetible (ejemplo: veterinario)

1. Cliente pide reservar un servicio vinculado a "Mascota" (tipo de objeto repetible).
2. El agente consulta las instancias existentes del cliente para ese negocio.
   - Si ya tiene una o más → pregunta cuál aplica, sin repetir el formulario.
   - Si no tiene ninguna → guía la creación de la primera instancia dentro del mismo flujo de reserva.
   - El cliente puede pedir explícitamente agregar una nueva instancia aunque ya tenga otras.
3. Resuelta la instancia, el agente continúa con los campos propios del servicio (si tiene) y procede con la reserva.

---

## 8. El agente como interfaz administrativa dual

### 8.1 Principio

El agente no es solo el canal por el que llegan clientes: es un **segundo consumidor de la misma API operativa**, actuando en nombre del negocio. Toda operación ya definida (crear/editar servicio, consultar disponibilidad, aprobar reserva, llenar formularios) se expone en dos modos:

- **Modo cliente:** reservar, consultar disponibilidad, pagar, llenar formularios de servicio.
- **Modo negocio/admin:** crear/editar servicios, ver reservas pendientes, aprobar/rechazar, gestionar contenido.

### 8.2 Vinculación de identidad

- Registro explícito de `empleado ↔ negocio ↔ número de WhatsApp ↔ rol`.
- Un número puede estar vinculado a más de un negocio; el agente desambigua contexto al inicio de la conversación cuando aplica.
- Al menos dos niveles de rol en el MVP: `administrador` (crea/edita servicios, gestiona verificación) y `operativo` (aprueba reservas del día a día), sin sistema de permisos granular completo.

### 8.3 Creación/edición conversacional de servicios

- El agente usa la plantilla de la categoría del negocio (sección 6) para guiar la conversación con preguntas relevantes al rubro, en vez de pedir campos genéricos.
- **Antes de confirmar**, el agente resume de vuelta lo entendido de forma estructurada ("Servicio: X, duración Y, precio Z, cupo N — ¿confirmas?"), evitando que una mala interpretación se publique directo.
- La confirmación es el punto de entrada al mismo pipeline de solicitud de contenido + filtro (sección 4) — no se duplica lógica entre el flujo conversacional y el flujo de moderación.

### 8.4 Notificaciones salientes hacia el negocio

A diferencia del resto del flujo (donde el agente responde), aquí el agente **inicia** la conversación: reserva nueva pendiente de aprobación, comprobante recibido (si aplica), etc. Reutiliza el mismo sistema de notificaciones/templates que se usaría para promociones (ver propuesta original, fase 2), ahora también disparado por eventos internos del negocio.

### 8.5 Auditoría

Cada acción ejecutada vía el agente en nombre de un empleado debe registrarse (usuario, acción, timestamp) — al no existir rastro visual de pantalla, este registro es indispensable para investigar disputas o errores.

### 8.6 Rol del dashboard web

Complementario, no el punto de entrada principal. Cubre lo incómodo de manejar por chat: cola de moderación de contenido, reportes de CRM/caja, configuración inicial más densa.

---

## 9. Modelo de pagos (revisado)

### 9.1 Cambio respecto a la propuesta original

Se descarta el modelo de 3 políticas (negocio / link / transferencia con comprobante) en favor de un modelo binario más simple:

| Política | Comportamiento |
|---|---|
| **Pago antes de confirmar** | El pago se coordina y ocurre antes de que el negocio confirme. El sistema no rastrea el pago; la aprobación de la reserva **no puede ser automática** — es forzosamente manual, porque la confirmación del negocio es en sí la señal de que se pagó. |
| **Pago después de confirmar** | El pago no bloquea nada; la reserva puede usar aprobación automática o manual según la configuración habitual del servicio. |

### 9.2 Mecanismo de coordinación

Cuando aplica "pago antes de confirmar", el agente comparte la tarjeta de contacto de WhatsApp del negocio con el cliente (funcionalidad estándar de WhatsApp). Negocio y cliente coordinan el pago directamente entre ellos, fuera del flujo de Atlas. El sistema vuelve a intervenir solo cuando el negocio aprueba la reserva.

### 9.3 Qué se elimina del alcance anterior

- Modelo de 3 políticas de pago
- Almacenamiento de adjuntos/comprobantes ligados a la reserva
- Estado de pago granular (`pendiente` / `comprobante recibido` / `confirmado` / `rechazado`)
- Registro de link de pago externo por parte del negocio como pieza del sistema

---

## 10. Casos de uso end-to-end

### 10.1 Alta de negocio → servicio → reserva → aprobación → pago

1. Negocio se registra (Etapa 1) → `pendiente de verificación`.
2. Negocio (vía agente o panel) crea un servicio, guiado por la plantilla de su categoría.
3. El filtro de contenido evalúa el texto; si no hay coincidencia, se publica de inmediato (aún no visible públicamente porque el negocio no está verificado).
4. En paralelo, el agente etiqueta el servicio para el sistema de recomendación.
5. Negocio completa verificación (Etapa 2, documentos según categoría) → equipo revisa → `verificado`.
6. Servicio queda visible para clientes reales.
7. Cliente reserva vía agente: si el servicio está vinculado a un objeto repetible, se resuelve la instancia; se llenan campos de formulario de servicio si existen.
8. Según la política de pago del servicio:
   - **Antes de confirmar:** agente comparte contacto del negocio; negocio y cliente coordinan pago; negocio aprueba manualmente cuando confirma el pago recibido.
   - **Después de confirmar:** la reserva sigue la configuración normal de aprobación (automática o manual) del servicio.
9. Negocio recibe notificación saliente de la reserva pendiente (si aplica aprobación manual) y confirma vía agente.

### 10.2 Edición de servicio con moderación

1. Negocio pide editar la descripción de un servicio vía agente.
2. Se crea una solicitud de edición (diff de campos).
3. El filtro corre sobre el texto modificado.
   - Sin coincidencia → se aplica de inmediato, versión publicada actualizada.
   - Con coincidencia → solicitud queda `en revisión`; versión publicada no cambia; negocio recibe notificación; equipo resuelve desde la cola de moderación.

---

## 11. Matriz de controles (resumen)

| Control | Dispara sobre | Automático / Manual | Efecto |
|---|---|---|---|
| Validación RNC/cédula (DGII) | Verificación de negocio | Automático (consulta) | Confirma identidad legal declarada |
| Revisión de documentos de verificación | Verificación de negocio | Manual | Cambia estado a `verificado` o rechaza |
| Filtro de contenido — negocio | Perfil de negocio | Automático (señal) + manual (decisión) | Asiste la revisión de verificación |
| Filtro de contenido — servicio/opción/extra | Creación/edición de servicio | Automático por defecto; manual si hay coincidencia | Publica o envía a `en revisión` |
| Solicitud de edición | Cualquier edición de servicio | Igual que arriba | Nunca oculta la versión publicada existente |
| Etiquetado para recomendación | Creación/edición de negocio/servicio | Automático, no bloqueante | Alimenta `NegocioTag`/`ServicioTag` |
| Reincidencia de rechazos | Historial de un negocio | Manual (señal) | Candidato a revisión de cuenta completa |
| Reporte de cliente | Post-reserva | Manual | Puede llevar a `suspendido` |

---

## 12. Mercado objetivo — tipos de negocio

Agrupados por **patrón de reserva**, ya que eso determina qué tan bien encaja el modelo diseñado (duración fija, capacidad, aprobación, formularios, objetos repetibles) — más que agruparlos solo por rubro.

### 12.1 Servicios personales de cita 1:1 — encaje casi perfecto con modo continuo (fase 1)

- Spas y masajes
- Salones de belleza / barberías
- Consultorios médicos y odontológicos (con licencias/exequátur, sección 3.2 y 6.3)
- Consultorios de psicología/terapia
- Podólogos, nutricionistas, fisioterapeutas
- Manicure/pedicure a domicilio o en local
- Tatuadores/estudios de tatuaje (buen caso de "requisitos previos" y formulario de servicio)

### 12.2 Servicios con objeto repetible del cliente (fase 2, sección 7.3)

- Veterinarias / peluquerías caninas (mascota como objeto repetible)
- Talleres mecánicos / centros de cambio de aceite (vehículo como objeto repetible)
- Servicios de mantenimiento de equipos (aires acondicionados, electrodomésticos)

### 12.3 Servicios grupales/clase — modo bloques fijos (fase 2)

- Estudios de yoga, pilates, spinning
- Academias de idiomas o música
- Gimnasios con clases dirigidas puntuales

### 12.4 Servicios profesionales/consultivos

- Abogados, contadores, asesores
- Coaches, consultores independientes
- Fotógrafos (sesión agendada + formulario de servicio para detalles)

### 12.5 Servicios de alojamiento/espacio (fase 2/3 — depende de "espacios compartidos")

- Salones de eventos pequeños / espacios de alquiler por hora
- Canchas deportivas, mesas de juego, estudios de grabación por hora
- Restaurantes con reserva de mesa (capacidad = mesas disponibles; el servicio reservable es el espacio, no la comida en sí)

### 12.6 Dónde el modelo encaja peor (para no sobre-vender el alcance)

- Negocios de **inventario de productos** sin componente agendable (retail puro)
- Negocios de **muy alto volumen y estandarización** con reglas de precio dinámico/overbooking complejas (cines, aerolíneas) — ya cubiertos por sistemas propios maduros
- Servicios de **emergencia/urgencia** (grúa, plomero de emergencia) — el patrón es disponibilidad inmediata, no agendamiento anticipado; es un problema de matching en tiempo real, distinto al diseñado aquí

### 12.7 Priorización sugerida

Los grupos 12.1, 12.2 y 12.3 son el **target primario** — validan cada pieza ya diseñada en fase 1/2. Espacios/eventos y restaurantes (12.5) quedan como expansión natural, condicionada a piezas de fase 2/3 (espacios compartidos, modo bloques fijos).

---

## 13. Próximos pasos

- Validar con el equipo el modelo binario de pago y confirmar que cubre los casos reales observados hoy.
- Definir el catálogo inicial de categorías con sus plantillas de verificación y de perfil.
- Definir el catálogo inicial de etiquetas de recomendación.
- Diseñar el contrato de operaciones de la API en modo negocio/admin (catálogo de acciones, precondiciones por rol, efectos).
- Definir el set inicial de reglas del filtro de contenido (lista negra por categoría).
