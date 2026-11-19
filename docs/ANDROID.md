# ATLAS en Android

ATLAS es una **PWA** (Progressive Web App): un solo código que se instala como app en Android e iPhone. En Android hay dos formas de tenerla:

## Opción 1: instalar desde Chrome (2 minutos)

1. En el celular Android abre **https://elias2111.github.io/atlas-chatbot-academico/** en **Chrome**.
2. Toca el menú **⋮** y luego **Instalar app** (o *Agregar a pantalla principal*).
3. Abre **ATLAS** desde el ícono: se ve a pantalla completa, sin barra del navegador, y funciona sin conexión.
4. Toca **INICIAR SISTEMA**, luego el núcleo, y permite el micrófono. En Android, Chrome usa el reconocimiento de voz de Google, así que la voz funciona bien también dentro de la app instalada.

## Opción 2: generar un APK con PWABuilder (10 minutos, sin Android Studio)

1. Entra a **https://www.pwabuilder.com** y pega la URL de la app.
2. Toca **Package for stores**, elige **Android** y luego **Generate package** (deja las opciones por defecto: *Trusted Web Activity*).
3. Descarga el `.zip`: trae el archivo **`.apk`** (para instalar directamente) y el `.aab` (para Google Play).
4. Pasa el `.apk` al celular, ábrelo y permite **Instalar apps de fuentes desconocidas** si lo pide.
5. Si al abrirla se ve una barra de dirección arriba, falta el archivo de verificación: copia el `assetlinks.json` que viene en el zip a `/.well-known/assetlinks.json` del sitio. Para la demo no es obligatorio.

## Probar en un emulador

En Android Studio, abre **Device Manager**, crea un dispositivo (por ejemplo Pixel 7, API 34) e inícialo. Luego arrastra el `.apk` sobre el emulador o abre Chrome dentro de él y sigue la opción 1. El micrófono del emulador se activa en **⋮ → Microphone → Virtual microphone uses host audio input**.

## Evidencia sugerida para la rúbrica

- Video corto o capturas del celular Android con la app instalada (ícono en la pantalla de inicio y app a pantalla completa).
- Consultas demostradas: matrícula ("¿Qué materias estoy viendo?"), estado académico ("Dame el informe del semestre"), proyección ("¿Cuándo me gradúo?") y recomendaciones ("Dame recomendaciones").
- Con n8n conectado: la etiqueta **"n8n · RAG"** sobre cada respuesta, que prueba que la app está conectada al webhook.
