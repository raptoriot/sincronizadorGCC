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

**SEGUNDA PARTE**
en esta parte vamos a crear un codigo para un dispositivo iot
pasos:
 carga rlos repositorios de requirementsIOT.txt 
 crear el nodo en la pagina junto con el registro y enlazarlo al topico pub/sub
 crear las llaves y subir la publica a l portal
 bajar cetificado
 (todo lo anterior en manual de notion)
 
 registro:casa-consumoTot
 tema:projects/asistente-180018/topics/casa-consumo
 dispositivo rasp1
 
 se creo la llave RS256_X509 
 se bajo el certificado wget https://pki.goog/roots.pem
 
 se ejecuta con lo siguiente
 python iotdevice.py \
      --project_id='asistente-180018' \
      --registry_id=casa-consumoTot \
      --device_id=rasp1 \
      --private_key_file=private-key.pem \
      --algorithm=RS256