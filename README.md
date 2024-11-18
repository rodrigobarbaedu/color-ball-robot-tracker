# 🤖 Robot Autónomo con Reconocimiento de Obstáculos y Reconocimiento de Pelotas de Colores

Este proyecto tiene como objetivo desarrollar un **robot autónomo** utilizando una **Raspberry Pi** junto con el kit de **Elegoo Smart Robot Car V4.0**. El robot es capaz de detectar pelotas de colores en su entorno utilizando **visión por computadora** y seguirlas de manera autónoma, evitando obstáculos en su camino. El sistema utiliza una cámara del Smart Robot Car para capturar imágenes en tiempo real y procesarlas con **OpenCV** para identificar las pelotas de colores. Una vez detectadas, el robot calcula la distancia y el ángulo hacia la pelota y ajusta su trayectoria para seguirla. Además, el robot es capaz de detectar obstáculos cercanos y detenerse para evitar colisiones. El proyecto combina conceptos de robótica móvil, visión por computadora y control autónomo para crear un robot inteligente y autónomo.

---

## Características principales:

- **Visión por Computadora:** Utiliza **OpenCV** para capturar imágenes de la cámara y procesarlas en tiempo real para identificar bolitas de colores específicos.
- **Autonomía en Movimiento:** El robot se mueve hacia la bolita de color detectada, adaptando su trayectoria para alcanzarla utilizando cálculos de distancia y ángulo basados en los datos obtenidos de la cámara.
- **Control del Robot:** El movimiento y la orientación del robot son controlados a través de comandos enviados a la placa base del Elegoo Smart Robot Car V4.0, con un control preciso de la velocidad y el ángulo de giro.
- **Hardware:** Utiliza una **Raspberry Pi** como cerebro del sistema, donde el Smart Robot toma fotogramas de la cámara, las envia a la Raspberry Pi para el procesamiento y toma decisiones de movimiento, estas decisiones son enviadas al Smart Robot para procesar el movimiento.
- **Detección de Obstáculos:** El robot es capaz de detectar obstáculos cercanos utilizando un sensor de ultrasonido y detenerse para evitar colisiones, reanudando su movimiento una vez que el obstáculo ha sido superado.

---

## Componentes utilizados:

- **Raspberry Pi:** Placa de desarrollo que actúa como el controlador principal del robot, ejecutando los scripts en Python y gestionando las operaciones de visión por computadora.
- **Elegoo Smart Robot Car V4.0:** Kit de robot con motores de Elegoo, ruedas y sensores de proximidad, utilizado para el movimiento y la navegación del robot.
- **Python & OpenCV:** Lenguaje de programación y biblioteca de visión por computadora para procesar las imágenes, detectar pelotas de colores y calcular la posición relativa del robot con respecto a la bolita, además de controlar el movimiento del robot.
- **Cámara:** Cámara ESP32-S3 para capturar imágenes en tiempo real y procesarlas para la detección de bolitas de colores.

---

## Funcionalidades del robot:

1. **Detección de Pelotas de Colores:** El robot es capaz de detectar pelotas de colores específicos en su entorno utilizando visión por computadora y OpenCV.
2. **Seguimiento de Pelotas:** Una vez que se detecta una pelota de color, el robot calcula la distancia y el ángulo hacia la pelota y ajusta su trayectoria para seguirla.
3. **Evitación de Obstáculos:** El robot es capaz de detectar obstáculos cercanos utilizando un sensor de ultrasonido y detenerse para evitar colisiones.
4. **Control de Movimiento:** El robot puede moverse hacia adelante, hacia atrás, girar a la izquierda y girar a la derecha, controlando la velocidad y el ángulo de giro.

---

## Objetivos de aprendizaje:

- **Robótica Móvil:** Aprender los conceptos básicos de la robótica móvil y cómo construir un robot autónomo utilizando una Raspberry Pi y un kit de robot.
- **Visión por Computadora:** Entender cómo utilizar OpenCV para procesar imágenes en tiempo real y detectar objetos de interés en un entorno.
- **Control Autónomo:** Implementar un sistema de control autónomo que permita al robot tomar decisiones de movimiento basadas en la información capturada por la cámara y los sensores.

---

## Requisitos previos:

- **Hardware:**
  - Raspberry Pi (Modelo 3B+ o superior recomendado).
  - Elegoo Smart Robot Car V4.0.

- **Software:**
  - Python 3.x. (Se recomienda la versión 3.7 o superior).
  - OpenCV.
  - Bibliotecas necesarias para la Raspberry Pi y el Elegoo Smart Robot Car.
  - Sistema operativo Raspbian instalado en la Raspberry Pi.
  - IDE o editor de código para programar en Python (por ejemplo, Thonny, VS Code, etc.).
  - Docker para creación de contenedores.

---

## Instalación:

1. Clona este repositorio:
  ```bash
   git clone https://github.com/rodrigobarbaedu/color-ball-robot-tracker.git
  cd color-ball-robot-tracker/Application/docker
  ```

2. (Requerimiento: Docker) Construye la imagen del contenedor:
  ```bash
   docker build --no-cache -t app-1 app-2
  ```

3. Ejecuta los contenedores:
  ```bash
  docker-compose up -d app-1 app-2
  ```

4. Accede a la dirección IP de la Raspberry Pi en un navegador web:
  ```bash
  http://<IP_Raspberry_Pi>:5050
  ```

5. ¡Listo! Ahora puedes ver la interfaz web del robot.
