# Workflow de orbitais no Node-RED

O fluxo [`orbitals.json`](orbitals.json) coordena a geração científica, a exportação no Blender e a gravação no Unity. Para configurar o ambiente e executar o primeiro teste, siga o [README principal](../README.md).

## Subflows

O botão **Gerar Job** recebe o nome de um preset em [`config/jobs/`](../config/jobs/), sem a extensão `.json`. O caminho principal percorre **Preparar Run → Científico → Blender → Unity** e termina no nó **Run concluída**.

| Subflow | Responsabilidade |
|---|---|
| **Preparar Run** | Chama `prepare_run`, que resolve o preset e cria `job.json`, `run.json` e os diretórios da execução. |
| **Científico** | Chama `scientific_runner` para calcular os orbitais e exportar malhas ou pontos em `scientific/`. |
| **Blender** | Executa `blender_runner.py` no Blender em segundo plano. Lê os dados científicos e grava os FBXs em `blender/`. A chamada inclui `--save-blend` para salvar também a cena preparada. |
| **Unity** | Chama `unity_runner` para abrir o editor, importar os modelos e gravar os GIFs em `unity/`. |
| **Recuperar e encaminhar** | Identifica a etapa interrompida e envia a Run para a entrada correspondente com `--resume`. |

## Mensagens entre etapas

**Preparar Run** lê o JSON emitido por `prepare_run` e mantém dois campos na mensagem:

- `msg.run_id` identifica a execução.
- `msg.run_dir` contém o caminho da pasta da execução.

Cada chamada prepara `msg.payload` com os argumentos que o próximo nó `exec` espera. No Científico, no Blender e no Unity, os nós de verificação leem o código de saída do processo e encaminham a mensagem quando o código é `0`. Os nós Debug de cada etapa mostram a saída normal e a saída de erro.

## Retomada e recuperação

| Estado da etapa em `run.json` | Ação |
|---|---|
| `failed` | Corrija a causa e coloque o ID da Run no botão **Retomar Científico**, **Retomar Blender** ou **Retomar Unity**, conforme a etapa. |
| `running` após uma interrupção | Confirme que o processo anterior encerrou. Preencha `run_id` e defina `confirm_stopped` como `true` no botão **Recuperar Run**. |
| `pending` após uma interrupção entre etapas | Execute a etapa pendente pelo terminal, sem `--resume`, conforme o [README principal](../README.md#executar-uma-run-pelo-terminal). |

As saídas de **Recuperar e encaminhar** seguem a ordem **1. Científico**, **2. Blender**, **3. Unity**. A retomada refaz a etapa científica ou Blender. No Unity, os GIFs concluídos e válidos podem ser reaproveitados.

## Atualizar o fluxo no repositório

1. Faça as alterações no editor e clique em **Deploy**.
2. Rode `test_single` e confira o GIF e o estado `completed` no `run.json`.
3. Antes de exportar, deixe `test_single` em **Gerar Job**, limpe os IDs dos botões de retomada e restaure `{"run_id": "", "confirm_stopped": false}` no botão de recuperação.
4. Exporte a aba em JSON formatado para `workflows/orbitals.json`, incluindo as definições dos subflows.