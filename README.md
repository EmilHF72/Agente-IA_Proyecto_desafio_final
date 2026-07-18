# ⚡ ElectroBot — Asistente Inteligente RAG

> **ElectroHogar Chile SpA** · Asistente conversacional con IA para consultas técnicas y administrativas.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-0052CC?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📋 Descripción

**ElectroBot** es un asistente inteligente basado en RAG (Retrieval-Augmented Generation) diseñado para **ElectroHogar Chile SpA**, empresa dedicada a:

- Mantención eléctrica domiciliaria
- Instalaciones y reparaciones eléctricas
- Certificaciones SEC
- Asesoría técnica basada en la Norma Técnica Chilena **RIC N°10**

### Modos de Operación

| Modo | Acceso | Fuente de Conocimiento |
|------|--------|----------------------|
| 🔓 **Público** | Sin autenticación | Norma RIC N°10 |
| 🔐 **Privado** | Empleados autenticados | Políticas Internas ElectroHogar |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Chat Area  │  │  Auth Panel  │  │  Sidebar   │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│              AgentExecutor (agente.py)               │
│    create_react_agent + ChatGroq + ConvBufferMemory  │
└──────┬───────────────────┬───────────────────────────┘
       │                   │
┌──────▼──────┐  ┌─────────▼──────────────────────────┐
│  validar_   │  │         consulta_RIC10()            │
│  empleado() │  │         consulta_politicas()        │
│  (autent.)  │  │    (retriever semántico FAISS)      │
└──────┬──────┘  └─────────┬──────────────────────────┘
       │                   │
┌──────▼──────┐  ┌─────────▼──────────────────────────┐
│ empleados   │  │      FAISS VectorStore              │
│    .csv     │  │  HuggingFace Embeddings (local)     │
└─────────────┘  │  RIC10.pdf + Politicas.pdf          │
                 └────────────────────────────────────┘
```

---

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|---|---|---|
| UI | Streamlit | ≥1.35 |
| LLM | Groq (LLaMA 3.3 70B) | — |
| Agente | LangChain ReAct | ≥0.2 |
| Vectorstore | FAISS CPU | ≥1.8 |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` | Local (sin API) |
| PDF Loader | PyPDF + LangChain | ≥4.3 |
| Datos | Pandas + CSV | — |

### Decisión de diseño: Embeddings multilingüe

Se usa `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` porque:
- Soporta español de forma nativa.
- Funciona completamente offline (sin API key).
- Es liviano (≈470MB) y compatible con Streamlit Community Cloud.
- Tiene mejor rendimiento semántico en español que `all-MiniLM-L6-v2`.

---

## 📁 Estructura del Proyecto

```
Proyecto_desafio_final/
├── app.py                  ← UI Streamlit principal
├── agente.py               ← AgentExecutor + ChatGroq
├── herramientas.py         ← LangChain Tools (3 herramientas)
├── autenticacion.py        ← Validación de credenciales
├── documentos.py           ← Carga y fragmentación de PDFs
├── prompts.py              ← System prompt + ReAct template
├── config.py               ← Configuración centralizada
├── vectorstore.py          ← FAISS + HuggingFace Embeddings
├── chat_memory.py          ← ConversationBufferMemory
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── datos/
│   └── empleados.csv       ← Base de datos de empleados
│
├── documentos/
│   ├── RIC10.pdf           ← Norma Técnica (acceso público)
│   └── Politicas_Internas_ElectroHogar.pdf  ← (acceso privado)
│
├── utils/
│   ├── __init__.py
│   ├── lector_pdf.py       ← Helper carga de PDFs
│   └── clasificador.py     ← Clasificador de intenciones
│
└── vectorstore_cache/      ← Índices FAISS (generado automáticamente)
    ├── ric10/
    └── politicas/
```

---

## 🚀 Instalación Local

### Requisitos previos

- Python 3.10 o superior
- [Groq API Key](https://console.groq.com) (gratuita)

### Paso a paso

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/electrobot-electrohogar.git
cd electrobot-electrohogar

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GROQ_API_KEY

# 5. Ejecutar la aplicación
streamlit run app.py
```

---

## ⚙️ Configuración

### Variables de Entorno

Copia `.env.example` como `.env` y completa:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Obtén tu API key gratuita en: https://console.groq.com

---

## ☁️ Deploy en Streamlit Community Cloud

1. **Sube el repositorio a GitHub** (asegúrate de incluir los PDFs en `documentos/`).

2. **Ingresa a** [share.streamlit.io](https://share.streamlit.io).

3. **Haz clic en "New app"** y selecciona tu repositorio.

4. Configura:
   - **Branch**: `main`
   - **Main file path**: `app.py`

5. En **"Advanced settings → Secrets"**, agrega:
   ```toml
   GROQ_API_KEY = "gsk_xxxxxxxxxx"
   ```

6. Haz clic en **"Deploy"**. ✅

> **Nota**: Los vectorstores FAISS se generan automáticamente en el primer arranque.
> Streamlit Cloud tiene soporte para `sentence-transformers` sin configuración adicional.

---

## 💬 Ejemplos de Uso

### Consultas Técnicas (sin autenticación)

**Usuario**: ¿Qué calibre de conductor usar para un circuito de 20A?
**ElectroBot**: Según la RIC N°10, para un circuito de 20A se recomienda conductor de sección...

**Usuario**: ¿Qué dice la norma sobre puesta a tierra?
**ElectroBot**: La RIC N°10 establece en su artículo... que toda instalación eléctrica...

**Usuario**: ¿Cuándo es obligatorio instalar un interruptor diferencial?
**ElectroBot**: Según la Norma RIC N°10, el interruptor diferencial es obligatorio en...

### Consultas Administrativas (con autenticación)

**Usuario**: ¿Cuántos días de vacaciones tengo?
**ElectroBot**: 🔐 Esta consulta requiere acceso de empleado. Por favor, inicia sesión.

*[Usuario ingresa: Carlos Muñoz / 1234]*

**ElectroBot**: ✅ Bienvenido, Carlos Muñoz (Gerente General).

**Usuario**: ¿Cuántos días de vacaciones tengo?
**ElectroBot**: Según las Políticas Internas de ElectroHogar, los empleados tienen derecho a...

---

## 📊 Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2025-07 | Release inicial — RAG dual-modo con autenticación |

---

## 📄 Licencia

MIT License — ElectroHogar Chile SpA © 2025

---

## 👥 Créditos

Desarrollado como proyecto final del curso **"Inteligencia de Datos y RAG Avanzado"** de Alura LATAM.

Tecnologías: LangChain · Groq · FAISS · Streamlit · HuggingFace · Python
