# prime-abundant-enumeration

> **¿Es tu primer contacto con el tema?** Hay una explicación desde cero,
> con dibujos y sin requisitos previos, en <https://jorgell23-sys.github.io/prime-abundant-enumeration/es/>
> (y en inglés en [`/`](https://jorgell23-sys.github.io/prime-abundant-enumeration/)).

<!-- hallazgo:que -->
## Qué se encontró

Los números prime-abundant —los `n` con `rad(n) | σ(n)`, la sucesión OEIS
A175200— se pueden listar **sin cribar**, porque la condición que los define
obliga a que todo primo de `n` aparezca al factorizar un valor de `σ`; eso lleva
la lista a `10^13` en vez de `10^7`, y da 85.695 términos donde había 10.000
publicados.

<!-- hallazgo:enunciado -->
## El enunciado

Sea `S(f) = { n : rad(n) | f(n) }` con `f` multiplicativa y **local**
(`p ∤ f(p^a)`), y sea `D_f(n)` el digrafo sobre los primos de `n` con flecha
`q → p` cuando `p | f(q^{v_q(n)})`.

- `n ∈ S(f)` **si y sólo si todo vértice de `D_f(n)` tiene flecha entrante**.
- Por lo tanto **ningún primo de `n` es libre**: cada uno divide a `f(q^a)` de
  otra potencia de primo de `n`. Y un digrafo finito con todos los grados de
  entrada `≥ 1` contiene un ciclo del que todo vértice es alcanzable.
- Entonces `S(f)(X)` se genera eligiendo ciclos dirigidos y agregando
  descendientes, con poda por `producto ≤ X`, y **si `q^a | n ≤ X` entonces todo
  otro primo de `n` es `≤ X/q^a`** — que es lo que mantiene barata la
  factorización.

Los conteos, con la fila de `10^9` ya publicada:

| `x` | prime-abundant | prime-perfect |
|---:|---:|---:|
| `10^9` | **5.328** | **198** |
| `10^10` | 11.051 | 333 |
| `10^11` | 22.295 | 513 |
| `10^12` | 44.157 | 796 |
| `10^13` | 85.696 | 1.212 |

<!-- hallazgo:ejemplo -->
## El caso más chico, hecho a mano

`n = 6 = 2·3`. Entonces `rad(6) = 6` y `σ(6) = 1+2+3+6 = 12`. Como `12 = 2·6`,
`rad(6) | σ(6)` y `6` es prime-abundant.

Leído como digrafo: `σ(2) = 3`, así que `2 → 3`; y `σ(3) = 4 = 2²`, así que
`3 → 2`. Los dos vértices tienen flecha entrante — ése es todo el criterio, y es
un ciclo de largo 2.

Y acá está el método. Desde `6` la búsqueda **no** prueba `7, 8, 9, …`. Pregunta
qué primos dividen a `σ(2³) = 1+2+4+8 = 15 = 3·5`: aparece el `5`, y `5` no
divide a `24 = 2³·3` (que es prime-abundant, porque `σ(24) = 60` y
`rad(24) = 6`). Entonces `24·5^c ∈ S(σ)` para todo `c ≥ 1` — en particular
`120`, el octavo término de A175200, donde `rad(120) = 30` y
`σ(120) = 360 = 12·30`. Después vienen `600` y `3000`. `verify.py` comprueba esa
consecuencia para `c = 1, 2, 3`.

El mismo razonamiento es lo que pone el menor elemento de `S(Φ₆)` en `100009` y
no en `39`: las mismas flechas, a exponentes más altos.

<!-- hallazgo:prueba -->
## Por qué es cierto

`p` es primo, así que divide a un producto si y sólo si divide a un factor;
aplicado a `rad(n) | f(n) = ∏ f(q^{v_q(n)})` da exactamente el criterio del
digrafo. Leído al revés, todo primo de `n` recibe una flecha, o sea que todo
primo de `n` es divisor primo de algún `f(q^a)` con `q^a || n`: ninguno es
libre. Retroceder por las flechas desde cualquier vértice no puede seguir para
siempre sin repetir, así que cierra un ciclo; luego todo vértice está en un
ciclo o después de uno. Y agregar un vértice ya cubierto no descubre a nadie,
porque los exponentes de los presentes no cambian — así que toda construcción
parcial es ya un elemento de `S(f)`, y la enumeración es completa.

<!-- hallazgo:comprobar -->
## Comprobalo vos

```
python verify.py
```

Sin dependencias, segundos. Imprime 38 líneas `PASS` y sale con 0. Dos de ellas
son **externas** — comparan contra números publicados por otras personas:

```
PASS  our terms up to 4320 equal the 49 published in A175200
PASS  prime-abundant up to 10^9 == 5328 (published)
PASS  prime-perfect up to 10^9 == 198 (published)
```

El anclaje publicado es Pollack y Pomerance, INTEGERS **12A** (2012), paper A14,
§1: *«up to 10^9, there are 198 prime-perfect numbers and 5328 prime-abundant
numbers.»*

<!-- hallazgo:nodice -->
## Qué NO dice

- **No dice que la idea de la enumeración sea nueva.** Sale directamente de la
  caracterización por digrafo, que no es nueva — Pollack y Pomerance ya usan los
  árboles `T(p)`, que son una restricción suya. No se encontró ningún enunciado
  publicado de esta enumeración, pero no encontrarlo no es evidencia. Está en
  `PRIOR_ART.md`. **Lo que sí es nuevo son los datos**: el b-file publicado
  termina en 7.271.402.112 y los conteos publicados llegan a `10^9`.
- **No da una asintótica.** El exponente efectivo `α = d log|S|/d log x` baja de
  0,45 a 0,288 en el rango medido y no se estabiliza; eso es compatible con las
  cotas conocidas y no prueba nada sobre el límite.
- **No predice `|S(f)(x)|` a partir de `f`.** Se descartaron seis invariantes
  candidatos, cada uno contra un criterio fijado de antemano. El mejor predictor
  hallado yerra un factor 2,3 fuera de muestra. Es un resultado negativo y se
  informa como tal.
- **El control exhaustivo llega a `10^10`, no a `10^13`.** Más allá de `10^10`
  cada término se verifica de a uno — lo que descarta falsos positivos, no
  falsos negativos.

---

## Qué hay acá

| | |
|---|---|
| `verify.py` | todos los controles, sin dependencias, en segundos |
| `src/enumerate_sf.py` | el enumerador, sólo biblioteca estándar |
| `data/` | los términos y los conteos, generados por código |
| `docs/` | **una explicación desde cero, para quien no conoce el tema** &mdash; publicada en <https://jorgell23-sys.github.io/prime-abundant-enumeration/es/> |
| `RESULT.md` | el enunciado completo, las pruebas y los límites |
| `PRIOR_ART.md` | qué se buscó, dónde, y el control positivo |

## Cómo citar

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22692700.svg)](https://doi.org/10.5281/zenodo.22692700)

> Ellena Godoy, Jorge (2026). *Prime-abundant numbers enumerated without
> sieving, to 10^13*. Zenodo. https://doi.org/10.5281/zenodo.22692700

El DOI de arriba es el DOI de **concepto** y siempre resuelve a la última
versión.

## Autor

**Jorge Ellena Godoy**

## Cómo se produjo

System design and research direction are the author's. The mathematical results
were produced by an automated system (Claude, Anthropic) under that direction.
All computations were verified by two independent implementations and
cross-checked against published work. The author is responsible for the
correctness of everything published here.
