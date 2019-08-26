# sincronizadorGCC
proyecto que sincroniza datos en GCC, usando pubsub, iot, sql 
Primer paso vamos a crear un programa que comienze a publicar por pub sub un numero aleatorio

**COMMIT 1**
En la primera version. se crea dos archivos, pub.py y sub.py (sacados de la carpeta de ejemplo)

se deben crear la variables de entorno
export GOOGLE_APPLICATION_CREDENTIALS=key.json
export proyecto='asistente-180018'

en este caso creamos el topico: casa-consumo 
la suscripcion: casa1-consumo-sub1

y los ejecutamos con

python sub.py $proyecto casa1-consumo-sub1
python pub.py $proyecto casa-consumo
