## Plano para usar tqdm mantendo modularização

### O que vamos fazer
- Criar uma camada de orquestração separada para gerar um orbital e salvar resultados
- Deixar `cli.py` responsável só por interface e visualização de progresso
- Manter `grid`, `physics` e `io` como módulos de domínio, sem lógica de interface
- Adicionar `tqdm` no CLI e opcionalmente no `save_batch` para acompanhar exportação interna

### Por que isso resolve
- A função que “usa praticamente todos os outros módulos” deve existir sim, mas como um orquestrador
- Isso preserva a modularização: cada módulo continua com responsabilidade única
- O CLI não precisa conter a lógica de cálculo, apenas monta e executa o fluxo

### Alterações-chave
- `src/generation.py` (novo)
  - `build_space(n)`
  - `compute_wavefunction(n,l,m,space)`
  - `compute_density(wavefunction, real, m)`
  - `generate_and_save_orbital(...)` ou funções similares

- `src/io/export.py`
  - adicionar argumento opcional de progresso em `save_batch`
  - usar esse callback/progress bar na iteração de níveis de isosuperfície

- `src/cli.py`
  - usar `tqdm` nos loops de geração de orbitais
  - passar a barra de progresso para `save_batch` quando gerar batch
  - ficar apenas com prompts e fluxo, sem cálculos nem exportação complexa

### Verificação
1. Rodar a geração automática e ver `tqdm` durante `n/l/m`
2. Verificar barra também durante `save_batch`
3. Confirmar que os `.obj` continuam corretos

### Observações
- Usar uma camada intermediária de orquestração não é anti-pattern; é o lugar certo para centralizar chamadas aos módulos `grid`, `physics` e `io`.
- `tqdm` deve ser importado no CLI e possivelmente passado como callback para `io/export.py`, assim o núcleo de cálculos não depende diretamente do pacote de progresso.
- O `cli` continua sendo responsável por interações de usuário; o restante deve oferecer APIs simples e testáveis.

### Considerações futuras
1. Se quiser depois, podemos separar ainda mais os comportamentos em `generate_orbital` e `save_orbital` para facilitar testes unitários.
2. Para uso em scripts ou notebooks, a camada de orquestração pode expor funções sem `tqdm`, recebendo callbacks opcionalmente.
