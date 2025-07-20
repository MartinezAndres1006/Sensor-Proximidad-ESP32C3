# 🔧 Sensor de Proximidad con ESP32, MicroPython y Adafruit IO

Este proyecto consiste en un sistema de medición de distancia utilizando un sensor ultrasónico **HCSR04**, una placa **ESP32**, y el lenguaje **MicroPython**. Los datos obtenidos se envían a la nube mediante el protocolo **MQTT** y son visualizados/controlados desde un **dashboard de Adafruit IO**. Además, el sistema activa una **alarma sonora** (buzzer) según los umbrales configurados remotamente.

---

## 🚀 Funcionalidades

- 📏 Lectura precisa de distancia con sensor **HCSR04**
- 🌐 Conexión WiFi + Envío de datos a **Adafruit IO**
- ☁️ Comunicación mediante **MQTT**
- 🔊 Alarma por buzzer PWM según cercanía del objeto
- 📊 Configuración de límites de distancia desde la nube
- 🔁 Reintento automático en caso de error o desconexión

---

## 📦 Componentes utilizados

| Componente        | Descripción                     |
|-------------------|---------------------------------|
| ESP32             | Microcontrolador WiFi/Bluetooth |
| HCSR04            | Sensor ultrasónico de distancia |
| Buzzer activo     | Alarma sonora                   |
| Jumpers y Protoboard | Conexión de componentes     |

---

## 📡 Conexiones

| Componente | Pin ESP32 |
|------------|-----------|
| Trigger    | GPIO 5    |
| Echo       | GPIO 18   |
| Buzzer     | GPIO 8    |
| VCC        | 3.3V      |
| GND        | GND       |

⚠️ Asegurate de usar divisores de voltaje o resistencias para no dañar el ESP32 con el pin **Echo** del HCSR04, ya que puede devolver 5V.

---

## 📊 Configuración del Dashboard en Adafruit IO

1. Crear una cuenta en (https://io.adafruit.com/)
2. Crear los siguientes **feeds**:
   - `distancia`
   - `alarma`
   - `distancia_min`
   - `distancia_med`
   - `distancia_max`
3. Armar un **dashboard** con:
   - Gráfico de línea para `distancia`
   - Texto o icono para `alarma`
   - Sliders o bloques numéricos para `distancia_min`, `distancia_med` y `distancia_max`

---
## 👨‍💻PREVIEW DEL PROGRAMA 
<img width="778" height="669" alt="Image" src="https://github.com/user-attachments/assets/d30a213d-8e60-4b21-81d4-53d234aeb691" />
<img width="869" height="694" alt="Image" src="https://github.com/user-attachments/assets/ad36b531-24cc-467a-b752-4da1a40e63b8" />
## 🧠 Lógica del programa

```python
if distancia < DISTANCIA_MIN:
    # Suena alarma grave
elif distancia < DISTANCIA_MED:
    # Suena alarma media
elif distancia < DISTANCIA_MAX:
    # Suena alarma leve
else:
    # Todo normal





