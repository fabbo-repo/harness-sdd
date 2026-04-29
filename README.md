# ejemplo-harness — Notes CLI

Proyecto de ejemplo que demuestra los principios de **Harness Engineering**
aplicados a un CLI minimalista de notas en Python.

> El código de la aplicación es deliberadamente simple. Lo importante de
> este repo no es **qué** hace, sino **cómo** está estructurado para que un
> agente de IA pueda trabajar sobre él de forma autónoma y verificable.

## Cómo está organizado el arnés

| Pilar | Manifestación en este repo |
|-------|----------------------------|
| **1. El repositorio ES el sistema** | `AGENTS.md`, `init.sh`, `feature_list.json`, `progress/`, `docs/` |
| **2. Orquestación multi-agente**    | `.claude/agents/leader.md`, `implementer.md`, `reviewer.md` |
| **3. Supervisión y mejora**         | `CHECKPOINTS.md`, hooks en `.claude/settings.json`, `tests/` |

## Para empezar

```bash
./init.sh
```

Si todo está verde, abre `AGENTS.md` y sigue desde ahí.

## Para usar la app (humanos)

```bash
python3 -m src.cli add "comprar pan" --body "y leche"
python3 -m src.cli list
```

## Probarlo tú mismo con Claude Code

Si te descargas el repo y abres Claude Code en la raíz, ya estás dentro del
arnés: `CLAUDE.md` fuerza al modelo a actuar como `leader` (orquesta, no
edita código).

Receta rápida:

1. `./init.sh` — debe terminar verde.
2. Abre `feature_list.json` y deja al menos una feature con `status: "pending"`.
   Si todas están en `done`, añade una nueva al final del array o cambia el
   estado de una existente para reabrirla.
3. Lanza Claude Code en la raíz del repo: `claude`.
4. Pídele literalmente: **«implementa la siguiente feature pendiente»**.

Lo que verás en chat:

- El **leader** anuncia el plan, lanza un `implementer` y luego un `reviewer`.
- Por chat **no pasa código** — solo referencias del tipo
  `done -> progress/impl_<feature>.md`. Esa es la regla anti-teléfono-descompuesto.

Dónde queda la traza de cada subagente (esto es la "visualización" persistente):

| Archivo                          | Quién lo escribe | Qué contiene                                        |
|----------------------------------|------------------|-----------------------------------------------------|
| `progress/current.md`            | leader           | Plan vivo de la sesión                              |
| `progress/impl_<feature>.md`     | implementer      | Archivos tocados + output de los tests              |
| `progress/review_<feature>.md`   | reviewer         | Checklist contra `docs/` y `CHECKPOINTS.md`         |
| `feature_list.json`              | implementer      | `pending` → `in_progress` → `done`                  |
| `progress/history.md`            | leader           | Resumen append-only al cerrar la sesión             |

Abre `progress/` en tu editor mientras Claude trabaja: cada informe aparece
en cuanto el subagente termina. Así puedes auditar paso a paso quién decidió
qué — el contenido no circula por chat, vive en disco y queda versionado.

## Estructura

```
.
├── AGENTS.md              # Mapa para agentes (divulgación progresiva)
├── CHECKPOINTS.md         # Criterios de "estado final correcto"
├── feature_list.json      # Alcance: una feature a la vez
├── init.sh                # Verificación e inicialización
├── progress/
│   ├── current.md         # Sesión activa (estado vivo)
│   └── history.md         # Bitácora append-only
├── docs/
│   ├── architecture.md    # Qué significa "buen trabajo"
│   ├── conventions.md     # Estilo, nombres, errores
│   └── verification.md    # Cómo demostrar que funciona
├── .claude/
│   ├── agents/            # Definiciones de líder, implementador, revisor
│   └── settings.json      # Hooks que automatizan la verificación
├── src/
│   ├── storage.py         # Persistencia atómica (JSON)
│   ├── notes.py           # Modelo de dominio
│   └── cli.py             # Interfaz argparse
└── tests/
    ├── test_storage.py
    ├── test_notes.py
    └── test_cli.py
```

## Aprendizajes que ilustra este proyecto

- **Divulgación progresiva** en `AGENTS.md`: el agente no recibe todas las
  reglas de golpe, recibe un mapa para buscarlas bajo demanda.
- **Una feature a la vez** validado por `init.sh` (rechaza más de un
  `in_progress` en `feature_list.json`).
- **Estado en disco**, no en chat: `progress/current.md` y `history.md`
  sobreviven a reinicios y context windows reventadas.
- **Verificación ejecutable**: `init.sh` corre los tests reales, no se fía
  de lo que diga el agente.
- **Patrón Líder-Trabajador-Revisor**: el líder no implementa, el
  implementador no se autoaprueba, el revisor no edita código.
- **Anti teléfono-descompuesto**: los subagentes escriben sus resultados
  en archivos y solo devuelven una referencia ligera.
