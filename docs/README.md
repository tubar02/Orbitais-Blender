# Documentação do Orbitais-Blender

## Diagramas

| Diagrama | Fonte | Figura vetorial da monografia |
|---|---|---|
| Arquitetura do pipeline | [PlantUML](diagramas/arquitetura.plantuml) | [PDF](diagramas/pdf/arquitetura.pdf) |
| Organização interna dos módulos Python | [Dependências](diagramas/modulos-dependencias.plantuml) e [classes](diagramas/modulos-classes.plantuml) | [PDF com os dois painéis](diagramas/pdf/modulos-python.pdf) |
| Sequência da execução no Unity | [PlantUML](diagramas/unity-sequencia.plantuml) | [PDF](diagramas/pdf/unity-sequencia.pdf) |
| Geometria do enquadramento no Unity | [TikZ](diagramas/unity-enquadramento-geometria.tex) | [PDF](diagramas/pdf/unity-enquadramento-geometria.pdf) |

### Visualizar os fontes PlantUML no VS Code

1. Em **Extensions** (`Ctrl+Shift+X`), instale [PlantUML, de jebbs](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml).
2. Abra um arquivo `.plantuml` desta pasta e pressione `Alt+D`. Pela paleta (`Ctrl+Shift+P`), o comando é **PlantUML: Preview Current Diagram**.
3. Mantenha [`estilo.iuml`](diagramas/estilo.iuml) ao lado dos fontes. Os quatro diagramas carregam esse arquivo.

Para renderização local no Windows, confira se `java -version` funciona no terminal do VS Code. A extensão já inclui o PlantUML e o Graphviz para Windows. O diagrama de enquadramento usa TikZ e pode ser consultado no PDF ou recompilado com LaTeX.

## Imagens e animações

- [Fluxo no Node-RED](media/fluxo-node-red.png)
- [Cena de demonstração no Blender](media/blender-layout.png)
- [Comparação das representações do orbital (4,2,2)](media/representacoes.png)
- [Três quadros da animação no modo signed](media/quadros-gif.png)
- [Orbital do hidrogênio em rotação](media/orbital-demo.gif)
- [Quadro B da comparação de parâmetros do Unity](media/unity-parametros-B.png), extraído do GIF piloto. O painel será completado com os quadros A e C.
