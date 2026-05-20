## Plano de ataque para desacoplar e modularizar o projeto

### O que está acontecendo hoje
- `src/physics/gera_orbitais.py` faz:
  - física de orbitais
  - geração de grade 3D
  - visualização Matplotlib
  - exportação de OBJ/Numpy
  - entrada interativa via `input()`
- `src/blender/point_cloud.py` faz:
  - leitura de dados
  - importação OBJ
  - criação de objetos Blender
  - organização de cena
  - materiais e visualização
- `src/utils/io_utils.py` é um utilitário de caminhos, mas o nome não reflete o que faz.

### Objetivo
Transformar o código em módulos menores com responsabilidades claras:
- física
- grade/coordinate
- IO de dados
- exportação de malha
- visualização
- integração Blender
- orquestração/CLI

---

## Estrutura proposta

`src/physics/`
- `atomic_orbitals.py` — normalização + funções de onda
- `density.py` — densidade de probabilidade
- `wavefunctions.py` (opcional) — funções de alta ordem

`src/grid/`
- `space.py` — `Grid3D`, `R`, `THETA`, `PHI`, parâmetros de resolução

`src/io/`
- `paths.py` — `get_data_path`, `ensure_dir`, `read_data_batch`
- `export.py` — `save_obj`, `save_points`, exportadores

`src/visualization/`
- `matplotlib_plot.py` — `plot_scalar_field`, slices, scatter 3D

`src/blender/`
- `io.py` — carregar `.obj`, `.npy`
- `scene.py` — coleções, mover objetos, arranjar grade
- `materials.py` — materiais e cores
- `scripts/` — scripts de teste separados

`src/cli.py`
- orquestração leve, aceitar parâmetros e chamar os módulos corretos

---

## Passos sugeridos

1. **Mapear responsabilidades atuais**
   - Lista de funções/postos do `gera_orbitais.py`
   - Identificar dependências de variáveis globais (`X, Y, Z, R, THETA, PHI`)

2. **Criar a estrutura de pacotes**
   - `src/grid/space.py`
   - `src/physics/atomic_orbitals.py`
   - `src/io/paths.py`
   - `src/io/export.py`
   - `src/visualization/matplotlib_plot.py`
   - `src/blender/io.py`
   - `src/blender/scene.py`
   - `src/blender/materials.py`
   - `src/cli.py`

3. **Extrair cálculos físicos**
   - mover `normalization`, `radial_part`, `angular_part`, `hydrogen_wavefunction`
   - manter a lógica exata, mas sem dependência de globals

4. **Extrair geração de grade**
   - encapsular `x, y, z, X, Y, Z, R, THETA, PHI` em uma classe ou função
   - usar parâmetros ao invés de variáveis globais

5. **Separar IO e exportação**
   - mover `save_to_file`, `save_obj`
   - `io.paths` para caminhos de dados
   - `io.export` para salvar arquivo e OBJ

6. **Separar visualização**
   - `plot_scalar_func` deve ir para `visualization/matplotlib_plot.py`
   - receber `grid` e `func` como argumentos, sem globals

7. **Reorganizar Blender**
   - separar leitura de arquivo, loading de OBJ e construção de cena
   - criar helpers de materiais e grid de objetos
   - mover `testa_pyblend.py` para um script de exemplo se necessário

8. **Criar entrypoint leve**
   - novo `src/cli.py` que usa os módulos acima sem lógica misturada
   - opcional: aceitar argumentos em vez de `input()`

---

## Verificação
1. garantir que a geração de um orbital continue funcionando
2. gerar `orbital_nX_lY_mZ.obj` e `.npy` com os novos módulos
3. carregar o OBJ no Blender com a rotina reorganizada
4. testar o novo CLI/entrada sem comportamento quebrado

---

## Arquivos-chave
- `src/physics/gera_orbitais.py`
- `src/blender/point_cloud.py`
- `src/utils/io_utils.py`
- `src/blender/testa_pyblend.py`

---

## Decisions
- O foco é modularizar sem alterar o domínio físico: manter as fórmulas de orbitais e a exportação.
- Não vamos misturar `Blender` com cálculo físico no mesmo módulo.
- O novo nome de módulo deve refletir a responsabilidade, não apenas o arquivo original.

---

## Further Considerations
1. Quer que eu sugira nomes de classes/serialized data para o projeto (`Orbital`, `Grid3D`, `MeshExporter`)?
2. Prefere manter o pacote raiz como `src` ou criar `orbitais/` dentro de `src` para uma separação ainda mais clara?
