# Usar una imagen oficial de Python como base
FROM python:3.12-slim

# Configurar el directorio de trabajo en el contenedor
WORKDIR /alquipiso/alquipiso

# Copiar el archivo de requerimientos al contenedor
COPY requirements.txt /alquipiso/alquipiso/

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . /alquipiso/

# Exponer el puerto en el que corre Django (puerto 8000 por defecto)
EXPOSE 8000

# Ejecutar las migraciones y correr el servidor de Django cuando se inicie el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
