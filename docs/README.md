# Documentação do Orbitais-Blender

## Monografia

[Consultar a monografia](monografia.pdf)

O PDF é adicionado separadamente à raiz de `docs/`, com o nome `monografia.pdf`.

## Diagramas

| Diagrama | Fonte | Figura vetorial da monografia |
|---|---|---|
| Arquitetura do pipeline | [PlantUML](diagramas/arquitetura.plantuml) | [PDF](diagramas/pdf/arquitetura.pdf) |
| Organização interna dos módulos Python | [Dependências](diagramas/modulos-dependencias.plantuml) e [classes](diagramas/modulos-classes.plantuml) | [PDF com os dois painéis](diagramas/pdf/modulos-python.pdf) |
| Sequência da execução no Unity | [PlantUML](diagramas/unity-sequencia.plantuml) | [Completo](diagramas/pdf/unity-sequencia.pdf) · [Preparação](diagramas/pdf/unity-sequencia-preparacao.pdf) · [Gravação](diagramas/pdf/unity-sequencia-gravacao.pdf) |
| Geometria do enquadramento no Unity | [TikZ](diagramas/unity-enquadramento-geometria.tex) | [PDF](diagramas/pdf/unity-enquadramento-geometria.pdf) |

### Visualizar os fontes PlantUML no VS Code

1. Em **Extensions** (`Ctrl+Shift+X`), instale [PlantUML, de jebbs](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml).
2. Abra um arquivo `.plantuml` desta pasta e pressione `Alt+D`. Pela paleta (`Ctrl+Shift+P`), o comando é **PlantUML: Preview Current Diagram**.
3. Mantenha [`estilo.iuml`](diagramas/estilo.iuml) ao lado dos fontes. Os quatro diagramas carregam esse arquivo.

Para renderização local no Windows, confira se `java -version` funciona no terminal do VS Code. A extensão já inclui o PlantUML e o Graphviz para Windows. O diagrama de enquadramento usa TikZ e pode ser consultado no PDF ou recompilado com LaTeX.

Os PDFs de preparação e gravação são os dois painéis do mesmo diagrama de sequência, separados para a diagramação da monografia. O fonte PlantUML e o PDF completo foram preservados.

## Imagens e animações

- [Fluxo no Node-RED](media/fluxo-node-red.png)
- [Cena de demonstração no Blender](media/blender-layout.png)
- [Comparação das representações do orbital (4,2,2)](media/representacoes.png)
- [Três quadros da animação no modo signed](media/quadros-gif.png)
- [Orbital do hidrogênio em rotação](media/orbital-demo.gif)
- [Game View e Inspector no Unity](media/unity-editor.png)
- [Comparação do enquadramento e da resolução](media/unity-parametros.png)
- [Quadro B do painel](media/unity-parametros-B.png), extraído do GIF piloto.


### Gravações do painel de parâmetros

O painel usa o orbital `(4,2,2)`, base real e modo `signed`, com A, B e C em uma única linha e quadros de mesma largura. A comparação A/B varia o enquadramento; B/C varia a resolução.
A imagem de 540 × 540 foi ampliada por vizinho mais próximo.

| Quadro | Run | screen_fill | Resolução |
|---|---|---|---|
| A | `run_20261105_041007_b4f2d7ec` | 0.70 | 1080 × 1080 |
| B | `run_20261104_110942_5de6180b` | 0.95 | 1080 × 1080 |
| C | `run_20261105_043243_fd7cebca` | 0.95 | 540 × 540 |
