# Apresentação e gravação dos orbitais no Unity

Este projeto importa os FBXs gerados pelo Blender, apresenta os modelos em rotação e grava animações GIF. Para configurar a versão do editor e executar uma Run completa, consulte o [README principal](../README.md).

## Cena e componentes

Abra [`Assets/Scenes/SampleScene.unity`](Assets/Scenes/SampleScene.unity). O objeto **Apresentador** contém o componente `OrbitalPresenter`. No Inspector, selecione os números quânticos, a base e a representação do orbital. Em Play Mode, use **Carregar orbital selecionado** no menu de contexto do componente para aplicar a seleção.

| Componente | Responsabilidade |
|---|---|
| [`OrbitalPresenter`](Assets/Scripts/OrbitalPresenter.cs) | Lê o catálogo, instancia o FBX selecionado e enquadra o modelo na câmera. |
| [`Rotation`](Assets/Scripts/Rotation.cs) | Gira o pivô do modelo pelos eixos Y, X e Z, um eixo por volta. |
| [`OrbitalRunImporter`](Assets/Editor/OrbitalRunImporter.cs) | Copia os FBXs de uma Run para o projeto e seleciona o catálogo dessa execução. |
| [`OrbitalRunSettings`](Assets/Editor/OrbitalRunSettings.cs) | Lê e valida as configurações Unity do `job.json`. |
| [`OrbitalRecordingRunner`](Assets/Editor/OrbitalRecordingRunner.cs) | Controla a entrada em Play Mode, espera o Apresentador ficar pronto e inicia a gravação. Também fornece a entrada usada pelo runner Python. |
| [`OrbitalGifRecorder`](Assets/Editor/OrbitalGifRecorder.cs) | Captura a Game View e grava os GIFs com o Unity Recorder. |
| [`OrbitalRecordingWindow`](Assets/Editor/OrbitalRecordingWindow.cs) | Abre a janela **Configurar gravações**, onde você escolhe a base e a representação e inicia a gravação em lote. |
| [`OrbitalRunCleanup`](Assets/Editor/OrbitalRunCleanup.cs) | Implementa os comandos de limpeza das Runs importadas. Remove as cópias dos FBXs em `Assets/Orbitals/` e preserva os arquivos originais em `runs/`. |

## Catálogos e menus

| Catálogo ativo | Origem dos modelos no projeto | Destino dos GIFs |
|---|---|---|
| Geral | `Assets/Orbitals/` | `Assets/Recordings/<representação>/` |
| Run importada | `Assets/Orbitals/<id>/` | `runs/<id>/unity/<representação>/`, na raiz do repositório |

No menu **Tools → Orbitais**, use **Importar FBX de uma Run** para inspecionar os modelos de uma execução. Use **Importar e gravar Run** para importar, carregar as configurações do Job e gravar o lote. **Usar catálogo geral** volta ao catálogo e ao destino padrão de gravação.

Para gravar o orbital em exibição, escolha **Gravar GIF** em Play Mode. Para gravar por base e representação, abra **Configurar gravações** e use **Gravar lote**.

## Parâmetros de uma Run

Os valores padrão estão em [`config/defaults.json`](../config/defaults.json) e podem ser ajustados no preset. O `job.json` da Run registra os valores efetivos.

| Campo | Parâmetros |
|---|---|
| `unity.presentation` | `rotation_speed` em graus por segundo, `screen_fill` e `revolutions`. |
| `unity.recording` | `fps`, `resolution` em pixels por lado, `quality` e `loop`. |

Para comparar gravações, registre os parâmetros do `job.json` que acompanhou cada saída.

## Arquivos de uma gravação

Durante uma Run, o GIF em produção fica em `_incomplete/`, dentro da pasta da representação. Quando a gravação termina e o arquivo passa pela verificação do Recorder, ele é movido para a pasta final. Uma retomada pode reaproveitar os GIFs finais válidos.

Se o Unity falhar numa execução automatizada, consulte `runs/<id>/unity/Editor.log`. Se o runner indicar que o Apresentador não ficou pronto, confira se a `SampleScene` está aberta e se o objeto **Apresentador** está presente.

Fora do Play Mode, **Limpar Run ativa** e **Limpar todas as Runs importadas** removem as cópias de FBX em `Assets/Orbitals/<id>/`. Os arquivos originais e os GIFs permanecem na pasta `runs/`.