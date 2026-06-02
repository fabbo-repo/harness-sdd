# project-spec.md — notes-cli

> Especificación **conversada**, no dictada. Cada sección nace de un debate
> entre el humano y el `spec_partner`: qué hace, cuál es el contrato exacto,
> qué casos límite existen y qué alternativas se descartaron y por qué.
> De aquí el `gherkin_author` destila `features/<name>.feature`.

## Propósito del proyecto

`notes-cli` es un gestor de notas minimalista por línea de comandos. El
código es deliberadamente simple: el repo enseña **proceso** (Harness
Engineering, edición artesano), no complejidad de dominio.

## Decisiones globales

- **Sin dependencias externas.** `requirements.txt` permanece vacío. Todo se
  hace con la stdlib (`argparse`, `json`, `tempfile`, `unittest`). Esto
  mantiene el arnés reproducible y permite el mutador casero
  (`tools/mutate.py`). *Alternativa descartada:* `click` + `pytest-bdd` —
  más ergonómico, pero introduce dependencias y oculta el mecanismo.
- **Almacén JSON atómico.** Las notas viven en un único archivo JSON
  (`NOTES_FILE`, por defecto `.notes.json`). La escritura es atómica
  (archivo temporal + `os.replace`). *Razón:* nunca dejar el archivo a
  medias si el proceso muere.
- **Contrato de errores uniforme.** Los errores de dominio (`NoteError`,
  `NoteNotFound`) se imprimen en **stderr** y devuelven **exit code != 0**.
  La salida útil va a **stdout**. Esto hace cada comando componible y
  testeable por su contrato observable.
- **Una nota = `{id, title, body, created_at}`.** `id` incremental,
  `created_at` en ISO 8601.

## Comandos

### `count` — contar notas  *(feature #8, en construcción)*

- **Propósito:** responder "¿cuántas notas tengo?" de un vistazo.
- **Comportamiento:** imprime un único entero, el total de notas.
- **Contrato:**
  - `python -m src.cli count` → stdout: el total como entero, exit code 0.
  - Almacén vacío o inexistente → stdout `0`, exit code 0.
  - El comando **no modifica** el archivo de notas (solo lectura).
- **Casos límite:**
  1. Sin archivo de notas → `0`.
  2. Archivo con N notas → `N` exacto (no "≥1", el número justo).
  3. Idempotente: ejecutarlo no cambia el almacén.
- **Decisiones:**
  - *Salida = entero pelado, sin texto* (`3`, no `Total: 3`). Razón:
    componible con `| wc`, `$(...)`, etc. *Alternativa descartada:* línea
    descriptiva — más amigable, menos componible. Gana componibilidad por
    coherencia con `list`/`recent`.
  - *Almacén inexistente cuenta como 0*, no como error. Razón: "no hay
    notas todavía" es un estado válido, no un fallo. Coherente con `list`,
    que tampoco falla si no hay notas.

### `recent` — N notas más recientes  *(feature #7, done)*

- **Propósito:** ver las últimas notas sin listar todo.
- **Contrato:**
  - `python -m src.cli recent` → hasta 5 notas, orden `created_at` desc.
  - `--limit K` cambia el número.
  - `--limit <= 0` → mensaje en stderr, exit code != 0.
  - Almacén vacío → no imprime nada, exit code 0.
  - Formato por línea: `<id>\t<created_at>\t<title>` (igual que `list`).
- **Decisión:** mismo formato que `list` para no inventar un segundo
  contrato de presentación.

### Comandos ya existentes (contrato resumido)

`add`, `list`, `show`, `delete`, `search`, `edit` — ver `src/cli.py`. Se
construyeron antes de adoptar este flujo; su contrato está implícito en sus
tests. No se reescriben salvo que una feature nueva los toque.

## Features pendientes (aún sin debatir en detalle)

- `cli_export` (#9) — exportar a Markdown.
- `cli_stats` (#10) — estadísticas agregadas.
- `cli_clear` (#11) — borrado destructivo con confirmación.

Cada una entrará por su propia conversación con el `spec_partner` antes de
tener `.feature`.

## Preguntas abiertas

_(ninguna por ahora)_
