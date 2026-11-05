# Modelagem tridimensional de orbitais atômicos em Blender e Unity

Projeto de Trabalho de Conclusão de Curso em Física Computacional no Instituto de Física de São Carlos da Universidade de São Paulo (IFSC-USP). O pipeline calcula orbitais do átomo de hidrogênio, gera representações tridimensionais e grava animações GIF destinadas à visualização em projetores holográficos.

O Python científico calcula a função de onda e exporta a geometria. O Blender prepara os objetos e exporta os FBXs. O Unity importa os modelos e grava as animações com o Recorder. O Node-RED coordena essas etapas e encaminha a retomada de execuções interrompidas.

| Representação | Base | Informação visualizada |
|---|---|---|
| `single` | Real ou complexa | Uma isosuperfície da densidade. |
| `signed` | Real | Superfícies associadas aos sinais positivo e negativo da função de onda. |
| `multilayer` | Real ou complexa | Isosuperfícies em vários níveis de densidade. |
| `point_cloud` | Real ou complexa | Pontos da grade dentro de uma faixa de densidade. |
| `phase` | Complexa | Isosuperfície de densidade com cores associadas a intervalos de fase. |

![Orbital do hidrogênio em rotação](docs/media/orbital-demo.gif)

## Escolha uma forma de execução

| Entrada | Uso |
|---|---|
| [Node-RED](#executar-pelo-node-red) | Executar o pipeline completo a partir de um preset. |
| [Terminal](#executar-uma-run-pelo-terminal) | Executar os mesmos runners por comando, etapa por etapa. |
| [CLI interativa](#explorar-orbitais-pela-cli) | Selecionar orbitais, explorar gráficos e exportar dados científicos. |
| [Scripts no Blender](#usar-os-scripts-no-blender) | Abrir os dados gerados pela CLI e exportar modelos FBX. |
| [Editor do Unity](#usar-o-editor-do-unity) | Inspecionar os modelos e gravar um orbital ou um lote pela interface. |

## Configuração no Windows

O ambiente científico usa NumPy, SciPy, scikit-image, tqdm e Rich. A CLI também usa Matplotlib. Se você já tem um ambiente Conda com essas dependências, pode ativá-lo. Para criar um ambiente separado:

```powershell
conda create -n orbitais python=3.12 pip
conda activate orbitais
python -m pip install numpy "scipy>=1.15" scikit-image tqdm rich matplotlib
```

O código usa `scipy.special.sph_harm_y`, introduzido no [SciPy 1.15](https://docs.scipy.org/doc/scipy/release/1.15.0-notes.html).

- **Blender.** Para rodar pelo terminal ou Node-RED, disponibilize `blender` no `PATH` e confira com `blender --version`. Os scripts Blender usam o Python interno do editor.
- **Unity.** Instale o Unity Editor **6000.5.7f1** e abra o projeto `unity/`. O manifesto do projeto declara URP **17.5.0** e Recorder **5.1.7**. Na primeira abertura, aguarde a importação dos pacotes e abra `Assets/Scenes/SampleScene.unity`.
- **Node-RED.** Com Node.js instalado, use `npm install -g node-red` para instalar o editor de workflows. O fluxo deste repositório usa nós integrados do Node-RED.

Para os dois caminhos automatizados, feche o projeto no Editor do Unity antes da execução. Na raiz do repositório, com o ambiente científico ativado, configure o caminho do editor no PowerShell:

```powershell
$env:UNITY_EXE = "C:\Program Files\Unity\Hub\Editor\6000.5.7f1\Editor\Unity.exe"
Test-Path $env:UNITY_EXE
```

Ajuste o caminho conforme a instalação. O `Test-Path` deve retornar `True`.

## Executar pelo Node-RED

1. No mesmo terminal, execute `node-red` a partir da raiz do repositório.
2. Abra [http://localhost:1880](http://localhost:1880) e importe [`workflows/orbitals.json`](workflows/orbitals.json) pelo menu **Import**.
3. Confira se o nó **Gerar Job** tem o payload `test_single`. Clique em **Deploy** e acione **Gerar Job**.
4. Aguarde **Run concluída** no painel Debug. A execução de teste gera um GIF do orbital \(1s\) na base real.

O nome no payload corresponde a um arquivo de [`config/jobs/`](config/jobs/), sem a extensão `.json`. Declare as bases no campo `basis` do preset. Use `overrides` para parâmetros como resolução da grade, número de camadas e gravação.

[`test_multi_basis`](config/jobs/test_multi_basis.json) produz 12 GIFs e exercita `multilayer` nas duas bases e `signed` na base real. [`full_n4_250`](config/jobs/full_n4_250.json) usa 250 pontos por eixo e prevê 240 GIFs para \(n=1\) a \(n=4\). Use `test_single` para conferir a instalação antes de iniciar o lote.

## Executar uma Run pelo terminal

Na raiz do repositório, com as dependências e `UNITY_EXE` configurados, execute no PowerShell:

```powershell
$prepared = python -m src.runners.prepare_run test_single
if ($LASTEXITCODE -ne 0) { throw "Falha ao preparar a Run." }
$run = ($prepared | ConvertFrom-Json).run_dir

python -m src.runners.scientific_runner --run "$run"
if ($LASTEXITCODE -ne 0) { throw "Falha na etapa científica." }

blender --background --python-exit-code 1 --python src/runners/blender_runner.py -- --run "$run" --save-blend
if ($LASTEXITCODE -ne 0) { throw "Falha na etapa Blender." }

python -m src.runners.unity_runner --run "$run"
if ($LASTEXITCODE -ne 0) { throw "Falha na etapa Unity." }

Write-Output "Resultados em $run"
```

`prepare_run` combina o preset com [`config/defaults.json`](config/defaults.json) e devolve o caminho da Run em JSON. Os três runners recebem esse mesmo caminho. A opção `--save-blend` também salva a cena preparada no Blender.

## Explorar orbitais pela CLI

Com o ambiente científico ativado, execute na raiz do repositório:

```powershell
python -m src.cli
```

A CLI permite escolher a base, gerar um orbital por \(n,l,m\) ou selecionar um intervalo de \(n\). No modo de orbital individual, também oferece visualizações da densidade com Matplotlib. As exportações manuais ficam em `data/<representação>/`. Para controlar `num_div`, use um preset e os runners.

## Usar os scripts no Blender

Com os dados científicos já exportados em `data/`, abra o script desejado no **Text Editor** do Blender e execute **Run Script**.

| Script | O que faz |
|---|---|
| [`src/blender/scripts/main.py`](src/blender/scripts/main.py) | Carrega um orbital. Em `main()`, ajuste `n`, `l`, `m`, `suffix` e `mode` conforme o arquivo exportado. |
| [`src/blender/scripts/show_all_obj.py`](src/blender/scripts/show_all_obj.py) | Carrega os orbitais de uma base e representação, organiza a cena e exporta os modelos. Ajuste a chamada `main(modo, base)` no fim do arquivo. |

Os scripts manuais exportam os FBXs para `unity/Assets/Orbitals/`, onde ficam disponíveis para o catálogo geral do Unity.

## Usar o Editor do Unity

Abra `unity/` no Unity e carregue a `SampleScene`. Na **Hierarchy**, selecione **Apresentador**. O componente `OrbitalPresenter` no **Inspector** expõe \(n,l,m\), base, representação, velocidade, preenchimento da tela e número de voltas. Com os modelos disponíveis no catálogo, entre no **Play Mode** e use **Carregar orbital selecionado**, no menu de contexto do componente, para aplicar a seleção. O mesmo menu oferece **Atualizar catálogo**.

No menu **Tools → Orbitais**:

| Comando | Ação |
|---|---|
| **Usar catálogo geral** | Usa os modelos em `Assets/Orbitals/` e restaura o destino padrão de gravação. |
| **Importar FBX de uma Run** | Seleciona uma pasta `runs/<id>/`, importa os FBXs dessa execução e ativa seu catálogo. |
| **Importar e gravar Run** | Importa os modelos, carrega os parâmetros do `job.json` e inicia a gravação do lote. |
| **Gravar GIF** | Grava o orbital que está sendo apresentado no Play Mode. |
| **Configurar gravações** | Abre a janela para escolher base e representação e acionar **Gravar lote**. |
| **Limpar Run ativa / Limpar todas as Runs importadas** | Remove as cópias importadas dentro de `Assets/Orbitals/`. |

O catálogo geral grava em `unity/Assets/Recordings/<representação>/`. Quando uma Run está ativa, a gravação vai para `runs/<id>/unity/<representação>/`.

## Resultados e retomada

| Caminho dentro de `runs/<id>/` | Conteúdo |
|---|---|
| `job.json` | Parâmetros efetivos da execução. |
| `run.json` | Estado geral, estados das etapas e eventual erro. |
| `scientific/<representação>/` | Malhas OBJ ou arquivos com coordenadas dos pontos. |
| `blender/<representação>/` | Modelos FBX. |
| `unity/<representação>/` | Animações GIF. |
| `unity/Editor.log` | Log do editor na execução pelo runner. |

No `test_single`, confira `status: "completed"` no `run.json` e o arquivo `unity/single/orbital_n1_l0_m0_real_single.gif` dentro da Run.

- **Etapa `failed`.** Corrija a causa e acione o nó **Retomar** correspondente com o ID da Run. Pelo terminal, repita o comando da etapa com `--resume`. Científico e Blender refazem a etapa. Unity reaproveita os GIFs válidos já produzidos.
- **Interrupção abrupta com etapa `running`.** Confirme que o processo anterior encerrou. No nó **Recuperar Run**, preencha `run_id` e defina `confirm_stopped` como `true`. Pelo terminal, use `python -m src.runners.recover_run --run "$run" --confirm-stopped` e depois retome a etapa indicada.
- **Interrupção entre etapas.** Se a próxima etapa está `pending`, execute seu comando sem `--resume` e prossiga com as etapas seguintes.

`runs/` e `data/` guardam artefatos locais. Para reproduzir uma figura, registre o commit utilizado e guarde o `job.json`, o `run.json` e o GIF da mesma execução.

## Documentação por componente

- [Workflow Node-RED](workflows/README.md)
- [Projeto Unity](unity/README.md)

## Monografia

A fundamentação teórica, os métodos e os resultados do projeto
estão descritos na [monografia](docs/monografia.pdf).

## Licença

O código autoral do projeto é distribuído sob a [Licença MIT](LICENSE.md). Os componentes de terceiros seguem suas respectivas licenças.
