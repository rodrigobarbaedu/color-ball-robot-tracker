# 🤖 Robot Autónomo con Reconocimiento de Bolitas de Colores

Este proyecto tiene como objetivo desarrollar un **robot autónomo** utilizando una **Raspberry Pi** junto con el kit de **Elegoo Smart Robot Car V4.0**. El robot está diseñado para reconocer y seguir bolitas de colores mediante el uso de **Python** y **OpenCV** para procesar las imágenes capturadas por la cámara del robot.

## Características principales:

- **Visión por Computadora:** Utiliza **OpenCV** para capturar imágenes de la cámara y procesarlas en tiempo real para identificar bolitas de colores específicos.
- **Autonomía en Movimiento:** El robot se mueve hacia la bolita de color detectada, adaptando su trayectoria para alcanzarla utilizando cálculos de distancia y ángulo basados en los datos obtenidos de la cámara.
- **Control del Robot:** El movimiento y la orientación del robot son controlados a través de comandos enviados a la placa base del Elegoo Smart Robot Car V4.0, con un control preciso de la velocidad y el ángulo de giro.
- **Hardware:** Utiliza una **Raspberry Pi** como cerebro del sistema, que se conecta a la cámara y controla el Elegoo Smart Robot Car V4.0. El robot es alimentado por una batería recargable, lo que le permite funcionar de manera autónoma durante varias horas.

## Componentes utilizados:

- **Raspberry Pi:** Placa de desarrollo que actúa como el controlador principal del robot, ejecutando los scripts en Python y gestionando las operaciones de visión por computadora.
- **Elegoo Smart Robot Car V4.0:** Kit de robot con motores, ruedas y sensores de proximidad, utilizado para el movimiento y la navegación del robot.
- **Python & OpenCV:** Lenguaje de programación y biblioteca de visión por computadora para procesar las imágenes, detectar bolitas de colores y calcular la posición relativa del robot con respecto a la bolita.
- **Cámara:** Cámara conectada a la Raspberry Pi para capturar imágenes y detectar colores en tiempo real.

## Funcionalidades del robot:

1. **Detección de bolitas de colores:** El robot es capaz de reconocer bolitas de colores utilizando un filtro de colores en el espacio de color HSV. Una vez detectada, calcula la distancia y el ángulo hacia la bolita.
2. **Movimiento hacia el objetivo:** El robot se mueve hacia la bolita detectada, ajustando su dirección según el cálculo del ángulo y la distancia.
3. **Evasión de obstáculos:** Además de seguir bolitas de colores, el robot es capaz de detectar obstáculos cercanos mediante sensores de distancia, deteniéndose automáticamente para evitar colisiones.
4. **Rotación de cámara:** La cámara del robot puede rotar para realizar un barrido y encontrar bolitas de colores en diferentes posiciones.

## Objetivos de aprendizaje:

- Aprender sobre robótica móvil y control autónomo.
- Introducción a la visión por computadora utilizando OpenCV.
- Integración de hardware y software en un proyecto de robótica.
- Desarrollo de algoritmos para la detección de objetos y el seguimiento en tiempo real.

## Requisitos:

- **Hardware:**
  - Raspberry Pi (Modelo 3B+ o superior recomendado).
  - Elegoo Smart Robot Car V4.0.
  - Cámara compatible con Raspberry Pi.

- **Software:**
  - Python 3.x.
  - OpenCV.
  - Bibliotecas necesarias para la Raspberry Pi y el Elegoo Smart Robot Car.

## Instalación:

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/robot_reconocimiento_bolitas.git
