import time
import machine
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient
from hcsr04 import HCSR04


# CONFIGURACIÓN DEL WIFI CON SU ID Y CONTRASEÑA


ssid = 'Wokwi-GUEST'
wifipassword = ''


# ACA CONFIGURAMOS EL ENTORNO PARA PODER ACCEDER A NUESTRO MQTT 


mqtt_server = 'io.adafruit.com'
port = 'El puerto de adafruit'
user = 'AndresAle1006'
#Agregar la contraseña de adafruit
client_id = 'MiSensorDistancia'

# EN ESTE APARTADO COLOCAMOS LOS FEEDS NECESARIOS PARA PODER RECIBIR Y ENVIAR DATOS DEL DASHBOARD
# topic_ALARMA = 'faqmatt/feeds/ALARMA3'
# topic_DISTANCIA = 'faqmatt/feeds/DISTANCIA'
# topic_DISTANCIA_MAX = 'faqmatt/feeds/DISTANCIAMAX'
# topic_DISTANCIA_MED = 'faqmatt/feeds/DISTANCIAMED'
# topic_DISTANCIA_MIN = 'faqmatt/feeds/DISTANCIAMIN'
# topic_ESTADO_SENSOR = 'faqmatt/feeds/ESTADO_SENSOR'

# ADAFRUIT ANDRES

topic_ALARMA = 'AndresAle1006/feeds/ALARMA3'
topic_DISTANCIA = 'AndresAle1006/feeds/DISTANCIA'
topic_DISTANCIA_MAX = 'AndresAle1006/feeds/DISTANCIAMAX'
topic_DISTANCIA_MED = 'AndresAle1006/feeds/DISTANCIAMED'
topic_DISTANCIA_MIN = 'AndresAle1006/feeds/DISTANCIAMIN'
topic_ESTADO_SENSOR = 'AndresAle1006/feeds/ESTADO_SENSOR'






# Estado de la alarma (POR DEFAULT LA DEJAMOS APAGADA)
ALARMA_ACTIVA = False

# ACA PUSIMOS LOS ESTADOS ESTANDAR, EN CASO EN QUE NO COLOQUEMOS ALGUN RANGO DE ENTRADA
DISTANCIA_MAX = 60
DISTANCIA_MED = 20
DISTANCIA_MIN = 6



# ACÁ SETEAMOS LO NECESARIO PARA ACCEDER A LOS LEDS MEDIANTE LAS SALIDAS DEL ESP 

Rojo = Pin(2, Pin.OUT)
Amarillo = Pin(1, Pin.OUT)
Verde = Pin(3, Pin.OUT)
LEDESTADO = Pin(7, Pin.OUT) #Este va a prender en el caso en que el sensor de proximidad este activo

#CONFIGURAMOS EL BUZZER CON SU FRECUENCIA
buzzer = PWM(Pin(8))
buzzer.freq(500)       
buzzer.duty_u16(0)   


# CONFIGURAMOS LAS SALIDAS DEL SENSOR DE DISTANCIA


sensor = HCSR04(trigger_pin=6, echo_pin=5)

# -------------------------------
# ACA SOLICITAMOS LA CONEXION AL WIFI
# -------------------------------

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, wifipassword)

print("Conectando al WiFi", end="")
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print("\nConectado:", sta_if.ifconfig())


# CALLBACK MQTT
# ACA ESTE CALLBACK NOS AYUDA A CONTROLAR QUE EXACTAMENTE ESTA PASANDO EN LA CONSOLA
#Y SE ENCARGA DE QUE SI HAY UN ERROR, SEA NOTIFICADO POR MEDIO DE LA COSOLA 

def callback_alarma(topic, msg):
    global ALARMA_ACTIVA, DISTANCIA_MAX, DISTANCIA_MED, DISTANCIA_MIN

    dato = msg.decode('utf-8')
    topicrec = topic.decode('utf-8')
    print("Cambio en", topicrec, ":", dato)

    if topicrec == topic_ALARMA:
        if "OFF" in dato.upper():
            ALARMA_ACTIVA = False
        else:
            ALARMA_ACTIVA = True

        LEDESTADO.value(ALARMA_ACTIVA)

    elif topicrec == topic_DISTANCIA_MAX:
        try:
            nuevo_max = int(dato)
            if nuevo_max > DISTANCIA_MED:
                DISTANCIA_MAX = nuevo_max
                print("Nuevo límite DISTANCIA_MAX:", DISTANCIA_MAX)
            else:
                print("Error: DISTANCIA_MAX debe ser mayor que DISTANCIA_MED")
        except:
            print("Error al leer DISTANCIA_MAX")

    elif topicrec == topic_DISTANCIA_MED:
        try:
            nuevo_med = int(dato)
            if DISTANCIA_MIN < nuevo_med < DISTANCIA_MAX:
                DISTANCIA_MED = nuevo_med
                print("Nuevo límite DISTANCIA_MED:", DISTANCIA_MED)
            else:
                print("Error: DISTANCIA_MED debe estar entre DISTANCIA_MIN y DISTANCIA_MAX")
        except:
            print("Error al leer DISTANCIA_MED")

    elif topicrec == topic_DISTANCIA_MIN:
        try:
            nuevo_min = int(dato)
            if nuevo_min < DISTANCIA_MED:
                DISTANCIA_MIN = nuevo_min
                print("Nuevo límite DISTANCIA_MIN:", DISTANCIA_MIN)
            else:
                print("Error: DISTANCIA_MIN debe ser menor que DISTANCIA_MED")
        except:
            print("Error al leer DISTANCIA_MIN")

# -------------------------------
# Hacemos la solicitud de la conexion del mqtt y suscribimos los topicos al mismo 
# -------------------------------

try:
    conexionMQTT = MQTTClient(client_id, mqtt_server, user=user, password=password, port=port)
    conexionMQTT.set_callback(callback_alarma)
    conexionMQTT.connect()
    conexionMQTT.subscribe(topic_ALARMA)
    conexionMQTT.subscribe(topic_DISTANCIA_MAX)
    conexionMQTT.subscribe(topic_DISTANCIA_MED)
    conexionMQTT.subscribe(topic_DISTANCIA_MIN)
    print("Conectado al broker MQTT")
except OSError as e:
    print("Error conectando al broker MQTT:", e)
    time.sleep(5)
    machine.reset()


# FUNCION PRINCIPAL DE NUESTRO PROYECTO


# Inicializamos el estado anterior y control de envío, esto nos sirve para no sobrecargar el 
#adafruit con mensajes innecesarios (Manda mensaje de actualizacion cada 5 seg o cuando haya un cambio de proximidad notoria)
estado_anterior = None
distancia_anterior = None
ultimo_envio = time.ticks_ms()
margen = 2  # cm de variación para volver a publicar distancia

while True:
    try:
        conexionMQTT.check_msg()
        time.sleep(1)

        estado_actual = None

        if ALARMA_ACTIVA:
            distancia = sensor.distance_cm()

            # Solo publica si cambió o pasaron 5s para que adafruit no lo bloquee
            if (
                distancia_anterior is None
                or abs(distancia - distancia_anterior) > margen
            ) and time.ticks_diff(time.ticks_ms(), ultimo_envio) > 5000:
                conexionMQTT.publish(topic_DISTANCIA, str(distancia))
                distancia_anterior = distancia
                ultimo_envio = time.ticks_ms()

            # Lógica de estados
            if distancia > DISTANCIA_MAX:
                estado_actual = "FUERA_DE_RANGO"
                Rojo.value(0)
                Amarillo.value(0)
                Verde.value(0)
                buzzer.duty_u16(0)

            elif DISTANCIA_MED < distancia <= DISTANCIA_MAX:
                estado_actual = "VERDE"
                Rojo.value(0)
                Amarillo.value(0)
                Verde.value(1)
                buzzer.duty_u16(0)

            elif DISTANCIA_MIN < distancia <= DISTANCIA_MED:
                estado_actual = "AMARILLO"
                Rojo.value(0)
                Amarillo.value(1)
                Verde.value(0)
                buzzer.duty_u16(0)

            else:
                estado_actual = "ROJO"
                Rojo.value(1)
                Amarillo.value(0)
                Verde.value(0)
                buzzer.duty_u16(20000)  # Enciende buzzer

            # Solo si el estado cambió, imprimir y publicar
            if estado_actual != estado_anterior:
                if estado_actual == "FUERA_DE_RANGO":
                    print("⚠️ Fuera de rango: distancia =", distancia, "cm")
                elif estado_actual == "VERDE":
                    print("✅ Distancia intermedia (verde):", distancia, "cm")
                elif estado_actual == "AMARILLO":
                    print("⚠️ Distancia cercana (amarillo):", distancia, "cm")
                elif estado_actual == "ROJO":
                    print("🚨 Peligro: distancia demasiado baja (rojo):", distancia, "cm")

                conexionMQTT.publish(topic_ESTADO_SENSOR, estado_actual)
                estado_anterior = estado_actual

        else:
            #Aca interactuamos con el dashboard para apagar el sensor y reiniciar todos los estados
            if estado_anterior is not None:
                print("⚪ Alarma desactivada. LEDs y buzzer apagados.")
                conexionMQTT.publish(topic_ESTADO_SENSOR, "ALARMA_OFF")
                estado_anterior = None

            Rojo.value(0)
            Amarillo.value(0)
            Verde.value(0)
            buzzer.duty_u16(0)

    except OSError as e:
        print("Error de ejecución:", e)
        time.sleep(5)
        machine.reset()
