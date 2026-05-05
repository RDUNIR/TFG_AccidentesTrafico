# Sistema de Gestión de Accidentes de Tráfico - Ávila

Aplicación de escritorio desarrollada en Python para la gestión, análisis y visualización de accidentes de tráfico en la provincia de Ávila. Trabajo de Fin de Grado.

**Autor:** Rodrigo Díaz Galán  
**Universidad:** Universidad Isabel I  
**Repositorio:** https://github.com/RDUNIR/TFG_AccidentesTrafico

---

## Requisitos previos

- Python 3.10 o superior
- PostgreSQL 14 o superior
- pgAdmin 4 (recomendado para importar la base de datos)

---

## Instalación paso a paso

### 1. Clonar el repositorio

```
git clone https://github.com/RDUNIR/TFG_AccidentesTrafico.git
cd TFG_AccidentesTrafico
```

O descargarlo directamente desde GitHub con el botón **"Code → Download ZIP"**.

### 2. Instalar las dependencias de Python

```
pip install -r requirements.txt
```

### 3. Crear la base de datos

Abre pgAdmin y sigue estos pasos:

1. Haz clic derecho sobre **Databases**
2. Selecciona **"Create → Database"**
3. Ponle el nombre: `db_tfe_accidentes`
4. Haz clic en **"Save"**

### 4. Importar la base de datos

1. Haz clic derecho sobre la base de datos **`db_tfe_accidentes`** recién creada
2. Selecciona **"Restore"**
3. En **"Filename"** selecciona el archivo `db_tfe_accidentes.sql` incluido en el repositorio
4. En **"Format"** selecciona **"Plain"**
5. Haz clic en **"Restore"**

Esto importará toda la estructura de tablas y los datos de prueba.

### 5. Configurar las credenciales

1. Crea un archivo llamado `.env` en la carpeta del proyecto
2. Copia el contenido del archivo `env.example` incluido en el repositorio
3. Rellena los valores con tus datos de conexión a PostgreSQL:

```
DB_HOST=localhost
DB_NAME=db_tfe_accidentes
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_PORT=5432
```

### 6. Ejecutar la aplicación

```
python main.py
```

---

## Módulos del sistema

- **Registro**: Alta, edición y eliminación de accidentes
- **Consulta**: Búsqueda y filtrado de registros con exportación
- **Gráficos**: Análisis estadístico visual con múltiples tipos de gráficos
- **Informes**: Generación de informes en PDF y Excel
- **Dispositivos**: Planificación operativa de controles de tráfico
