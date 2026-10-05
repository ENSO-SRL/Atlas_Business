# Resumen de Metadatos Extra por Vertical

Este documento resume todos los campos de metadatos exclusivos que hemos implementado para cada vertical de negocio, tanto en el proceso de creación del establecimiento (Onboarding) como en la creación de sus servicios y cupos reservables.

---

## 🍽️ Restaurantes

### 1. Creación del Negocio (Onboarding)
*Contexto general sobre la experiencia y facilidades del local.*
- **Áreas del restaurante:** Lista dinámica gestionable.
- **Opciones de pago:** Lista dinámica gestionable.
- **Precio referencial:** Rango o monto aproximado.
- **Estilo de la experiencia:** (Dining Style).
- **Estilo Gastronómico.**
- **Personal Relevante:** (Chef reconocido, etc.).
- **Código de Vestimenta.**
- **Mascotas y Niños:** ¿Aceptan mascotas? ¿Se permiten niños? (Toggles).
- **Facilidades:** ¿Tiene Valet Parking? (Toggle).
- **Servicios Extra / Menú:** Servicios adicionales dentro del local no gestionables en Atlas (incluye descripción, horario, items con nombre, precio e ingredientes).

### 2. Creación del Servicio (Wizard)
*En restaurantes, el servicio suele representar el concepto o el espacio general ofrecido al comensal.*
- **Nombre del Servicio:** (Ej. Menú Ejecutivo, Mesa Privada).
- **Área del Restaurante:** En qué parte del local se ofrece este servicio en particular.

### 3. Creación de Cupo/Lugar (Mesas)
*Metadatos específicos para cada mesa individual.*
- **Área de la mesa:** Ubicación exacta (Ej. Terraza, Ventana).
- **Accesibilidad:** ¿Adaptada para silla de ruedas? (Toggle).
- **Combinabilidad:** ¿Puede unirse a otras mesas? (Toggle).
- **Unificable con:** Especificar con cuáles mesas se puede juntar (visible solo si la anterior es "Sí").

---

## 🎾 Pádel

### 1. Creación del Negocio (Onboarding)
*Información sobre las facilidades del club deportivo.*
- **Descripción del club** y **Áreas del club**.
- **Nivel de jugadores:** Orientación (Principiante, Intermedio, Avanzado).
- **Facilidades (Toggles):** Estacionamiento, Vestidores, Duchas, Baños, Cafetería/Restaurante, Tienda deportiva.
- **Servicios Integrados (Toggles):** Alquiler de palas, alquiler/venta de pelotas, oferta de clases, organización de torneos.
- **Personal relevante:** Entrenadores, profesores, jugadores/profesionales asociados.
- **Reglas generales** y **Métodos de pago**.
- **Servicios Extra:** Servicios del club no gestionables en Atlas.

### 2. Creación del Servicio (Wizard)
*El servicio se denomina "Tipo de Cancha".*
- **Nombre del Tipo de Cancha:** (Ej. Cancha Premium, Cancha de Cristal).
- **Descripción:** Detalles sobre el césped, paredes, material, etc.
- **Techada:** ¿Es una cancha techada (Indoor)? (Toggle).

### 3. Creación de Cupo/Lugar (Canchas Individuales)
- *Aún no se han definido metadatos extra a nivel de objeto para este vertical. Utiliza los datos base (Nombre, Capacidad).*

---

## ⛳ Golf

### 1. Creación del Negocio (Onboarding)
*Configuración expansiva para clubes de golf.*
- **Descripción del club** y **Áreas del club**.
- **Políticas de Acceso:** ¿Acepta acompañantes no miembros? (Toggle).
- **Facilidades (Toggles):** Clubhouse, Estacionamiento, Vestidores, Duchas, Restaurante/Bar, Tienda/Pro Shop.
- **Áreas de Práctica (Toggles):** Driving range, Putting green, Área de práctica general.
- **Servicios Integrados (Toggles):** Alquiler de palos, Alquiler de carritos, Alquiler de caddies, Oferta de clases.
- **Personal relevante:** Profesionales/Instructores.
- **Reglas generales**, **Código de vestimenta** y **Métodos de pago**.
- **Servicios Extra:** Servicios del club no gestionables en Atlas.

### 2. Creación del Servicio (Wizard)
*El servicio se denomina "Campo", asumiendo la venta de Green Fees o accesos.*
- **Nombre del Campo:** (Ej. Campo Norte, Campo Sur).
- **Descripción del Campo:** Dificultad, diseño, lagos, etc.
- **Cantidad de Hoyos:** Selector restringido a 9 o 18 hoyos.

### 3. Creación de Cupo/Lugar (Tees / Salidas)
- *El concepto genérico de "Cupo" se renombra automáticamente a "Tee / Salida". Aún no se han definido metadatos extra a nivel de objeto para este vertical.*
