# LMOT Knowledge Matrix

**Living Manual of Things** -- Et modulaert vidensbibliotek designet til mennesker og AI-agenter.

---

## Hvad er dette?

LMOT Knowledge Matrix er et struktureret vidensbibliotek, der indeholder dybdegaaende Knowledge Units inden for tre kernedomaener:

| Domaine | Prefix | Beskrivelse |
|---------|--------|-------------|
| Teknologi | `TECH-` | Espressoteknologi, maskinparametre, ekstraktion |
| Kultur | `CUL-` | Madkultur, tilberedningsteknikker, traditioner |
| Videnskab | `SCI-` | Fermentering, kemi, mikrobiologi |

## Hurtig navigation

- **[INDEX.csv](INDEX.csv)** -- Komplet katalog over alle Units (ID, emne, version, status)
- **[/units](units/)** -- Selve vidensbiblioteket
- **[/schemas](schemas/)** -- Teknisk dokumentation og JSON-schema

## Saadan bruger du dette repo

### For mennesker
Brug `INDEX.csv` til at finde det emne du soeger, og naviger derefter til den relevante mappe under `/units/`.

### For AI-agenter og MCP-servere
1. Leas `INDEX.csv` for at faa et komplet overblik over tilgaengelige Units
2. Hent den relevante `unit.md` fra `/units/{UNIT-ID}/`
3. Hver unit indeholder en struktureret JSON-metadata-blok der foelger `schemas/mcp-technical-v1.json`

## Struktur

```
/LMOT-Knowledge-Matrix
|
|-- README.md               <-- Du er her
|-- INDEX.csv               <-- Katalog over alle Units
|-- LICENSE                 <-- Licensaftale
|
|-- /units                  <-- Vidensbiblioteket
|   |-- /TECH-ESP-001      <-- Espresso: Grundlaeggende ekstraktion
|   |-- /CUL-ASADO-001     <-- Asado: Traditionel argentinsk grill
|   |-- /SCI-FERM-001      <-- Fermentering: Grundlaeggende principper
|
|-- /schemas                <-- Teknisk dokumentation
    |-- mcp-technical-v1.json
```

## Versionsstyring

Hver Unit har sin egen version (f.eks. `1.0`, `1.1`). Naar en Unit opdateres:
1. Indholdet rettes direkte i den eksisterende fil
2. `version` opdateres i JSON-blokken og i `INDEX.csv`
3. Et commit laves med beskrivende tekst, f.eks.: *"Update: Improved thermal variables for high-altitude Asado (v1.4)"*

Git-historikken bevarer alle tidligere versioner, mens den nyeste version altid er tilgaengelig direkte.

## Licens

Se [LICENSE](LICENSE) for detaljer.
