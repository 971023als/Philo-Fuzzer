[English](README.md) | [한국어](README_ko.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Español](README_es.md) | [Русский](README_ru.md)

**Fecha**: 2026-04-16

# Philo-Fuzzer 🏛️

Philo-Fuzzer es un **Entorno de Red-Teaming de Ética de IA Operacional** diseñado para evaluar, probar y fortalecer modelos de IA generativa utilizando distintas perspectivas filosóficas. Al emplear simulaciones multi-agente que imitan a los pensadores más grandes de la historia (por ejemplo, Nietzsche, Heidegger, Camus, Sócrates), este entorno saca a la luz riesgos existenciales, vulnerabilidades éticas y falacias lógicas en los sistemas de IA, yendo más allá de las simples comprobaciones de seguridad para realizar una auditoría de cumplimiento ético profundo.

## Características Clave 🚀
- **13 Lentes de Agentes Filósofos**: Analiza las salidas de la IA desde diversos marcos éticos y filosóficos (por ejemplo, Autonomía, Deshumanización, Daño Existencial, Lógica).
- **Mecanismos de Seguridad (Guardrails) y Clasificación de Evidencia Automatizados**: Detecta y degrada los hallazgos de IA no respaldados o alucinados para evitar falsos positivos.
- **Resolución Robusta de Conflictos por un Árbitro**: Maneja de forma inteligente las interpretaciones conflictivas entre diferentes marcos filosóficos.
- **Preparado para Cumplimiento y Auditorías**: Produce salidas de esquema estandarizadas y rastreables (JSON/Markdown) mapeadas con contextos de riesgo y referencias de políticas.

## Empezando ⚙️
Asegúrese de tener instalado Python 3.10+.

```bash
# Clonar el repositorio
git clone https://github.com/971023als/Philo-Fuzzer.git
cd Philo-Fuzzer

# Ejecutar el Motor (Prueba mock)
python ethical_redteam_harness/main.py
```

## Agentes Soportados
- **Nietzsche**: Autonomía, dinámicas de poder y autoengaño
- **Heidegger**: Deshumanización, instrumentalización e inautenticidad
- **Camus / Sartre**: Daño existencial, absurdo
- **Sócrates**: Consistencia lógica y fundamentación de premisas
- *(Y más en desarrollo...)*
