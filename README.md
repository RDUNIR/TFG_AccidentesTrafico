# Sistema de Gestión de Accidentes de Tráfico - Ávila

Aplicación de escritorio desarrollada en Python para la gestión, análisis y visualización de accidentes de tráfico en la provincia de Ávila. Trabajo de Fin de Grado.

## Requisitos

- Python 3.10 o superior
- PostgreSQL

## Instalación

1. Clona el repositorio:
```
git clone https://github.com/RDUNIR/TFG_AccidentesTrafico.git
```

2. Instala las dependencias:
```
pip install -r requirements.txt
```

3. Crea el archivo `.env` a partir del archivo de ejemplo:
```
cp .env.example .env
```

4. Rellena el archivo `.env` con los datos de tu base de datos.

5. Ejecuta la aplicación:
```
python main.py
```

## Módulos

- **Registro**: Alta y edición de accidentes
- **Consulta**: Búsqueda y filtrado de registros
- **Gráficos**: Análisis estadístico visual
- **Informes**: Generación de informes en PDF y Excel
- **Dispositivos**: Planificación operativa de controles

## Autor

Rodrigo Díaz Galán
