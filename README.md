# Compiladores

Repositório com a implementação incremental de um compilador/interpreter para uma linguagem funcional de expressões. O projeto foi desenvolvido em Python como uma sequência de atividades práticas (`vpl1` a `vpl15`), evoluindo desde a análise léxica até a geração de código, interpretação de instruções de baixo nível e alocação de registradores.

## Objetivos

- Implementar um analisador léxico para a linguagem.
- Construir e avaliar uma árvore de sintaxe abstrata (AST).
- Implementar um parser descendente recursivo com precedência de operadores.
- Adicionar variáveis, escopos lexicais, expressões `let` e condicionais.
- Avaliar expressões usando o padrão Visitor.
- Detectar variáveis não definidas e erros de tipo.
- Inferir tipos por geração e unificação de restrições.
- Suportar funções anônimas, aplicação de funções e funções recursivas.
- Gerar instruções de uma máquina abstrata semelhante a um subconjunto de RISC-V.
- Otimizar o código gerado por meio de alocação de registradores.

## Organização do repositório

Cada diretório `vplN` representa uma etapa independente do desenvolvimento do compilador. Os arquivos possuem nomes semelhantes entre as etapas porque a implementação é construída progressivamente.

```text
compiladores/
├── vpl1/                  # Analisador léxico inicial
│   ├── Lexer.py
│   └── driver.py
├── vpl2/                  # AST e avaliação direta de expressões
│   ├── Expression.py
│   └── driver.py
├── vpl3/                  # Lexer + parser de expressões aritméticas
├── vpl4/                  # Variáveis, let e escopos léxicos
├── vpl5/                  # Padrão Visitor, avaliação e análise uso-definição
├── vpl6/                  # Verificação estática de tipos
├── vpl7/                  # Geração de restrições para inferência de tipos
├── vpl8/                  # Funções anônimas, aplicação e tipos
├── vpl9/                  # Avaliação e análise de expressões funcionais
├── vpl10/                 # Parser da linguagem funcional tipada
├── vpl11/                 # Geração e execução de instruções de baixo nível
├── vpl12/                 # Renomeação de variáveis antes da geração de código
├── vpl13/                 # Geração de código para a máquina abstrata
├── vpl14/                 # Geração de código com memória e controle de fluxo
├── vpl15/                 # Alocação de registradores e otimização
└── .gitignore
```

As etapas compartilham uma arquitetura conceitual baseada em quatro componentes principais:

- **`Lexer.py`**: transforma o texto de entrada em tokens, reconhecendo números, booleanos, identificadores, operadores, comentários e palavras-chave.
- **`Parser.py`**: transforma a sequência de tokens em uma AST, respeitando a precedência dos operadores.
- **`Expression.py`**: define os nós da AST, como `Num`, `Bln`, `Add`, `Let`, `IfThenElse`, `Fn` e `App`.
- **`Visitor.py`**: implementa operações sobre a AST, incluindo avaliação, verificação de tipos, inferência e geração de código.

Nas etapas finais, o fluxo é semelhante a:

```text
texto-fonte
    ↓
Lexer
    ↓
tokens
    ↓
Parser
    ↓
AST
    ↓
renomeação / análise semântica
    ↓
geração de instruções
    ↓
alocação de registradores
    ↓
interpretador da máquina abstrata
    ↓
resultado
```

## Linguagem suportada

A linguagem evolui ao longo das etapas. Entre os recursos implementados nas versões mais avançadas estão:

- Literais inteiros e booleanos: `42`, `true`, `false`.
- Operadores aritméticos: `+`, `-`, `*` e divisão inteira.
- Comparações: `<`, `<=` e igualdade.
- Operadores booleanos: `and`, `or` e `not`.
- Negação aritmética com `~`.
- Expressões locais com `let`:

```text
let x <- 10 in x + 2 end
```

- Condicionais com `if`, `then` e `else`.
- Funções anônimas com `fn` e aplicação de funções.
- Tipos `int`, `bool` e tipos função.
- Comentários de linha iniciados por `--`.
- Comentários de bloco delimitados por `(*` e `*)`.
- Literais binários, octais e hexadecimais nas etapas do lexer que os suportam.

A gramática e os tokens disponíveis podem variar entre as versões. Para estudar um recurso específico, consulte o `Lexer.py`, `Parser.py` e `Expression.py` do respectivo diretório `vplN`.

## Requisitos

- Python 3.
- Nenhuma dependência externa é necessária: o projeto utiliza apenas a biblioteca padrão do Python, incluindo `abc`, `enum`, `sys` e `collections`.

Não há `requirements.txt`, `pyproject.toml`, `setup.py` ou outro arquivo de empacotamento. Por isso, cada etapa deve ser executada diretamente a partir do seu próprio diretório.

## Como executar

### Executar uma etapa com o driver

Entre no diretório da etapa desejada e envie a expressão pela entrada padrão. Por exemplo, para testar o parser e avaliador da `vpl4`:

```bash
cd vpl4
printf '1 + 2 * 3\n' | python3 driver.py
```

Saída esperada:

```text
Value is 7
```

As etapas posteriores seguem o mesmo padrão geral, embora o formato da saída possa mudar. Por exemplo, a `vpl11` imprime o resultado da execução da máquina abstrata, enquanto as etapas `vpl13` a `vpl15` passam também por geração de código.

```bash
cd vpl11
printf '1 + 2 * 3\n' | python3 driver.py

cd ../vpl15
printf '1 + 2 * 3\n' | python3 driver.py
```

### Executar os doctests

Os módulos contêm diversos exemplos executáveis em formato doctest. Para verificar uma etapa:

```bash
cd vpl15
python3 -m doctest *.py
```

Para testar outra etapa, substitua `vpl15` pelo diretório correspondente. Alguns arquivos dependem de módulos da própria etapa; por isso, execute o comando dentro do diretório, e não a partir da raiz do repositório.

### Testar o lexer isoladamente

A `vpl1` imprime o tipo de cada token reconhecido:

```bash
cd vpl1
printf '10 + 0xA -- comentário\n' | python3 driver.py
```

### Testar a análise de uso e definição

A `vpl5` possui três modos no `driver.py`:

```bash
cd vpl5
printf 'eval 1 + 2 * 3\n' | python3 driver.py
printf 'usedef let x <- 10 in x + 1 end\n' | python3 driver.py
printf 'safe_eval let x <- 10 in x + 1 end\n' | python3 driver.py
```

- `eval`: avalia a expressão.
- `usedef`: verifica se existem variáveis usadas antes de serem definidas.
- `safe_eval`: executa a análise de variáveis livres antes da avaliação.

## Componentes principais das etapas finais

### Máquina abstrata

`vpl11/Asm.py` e as versões seguintes implementam a classe `Program`, que mantém:

- Ambiente de registradores e variáveis.
- Contador de programa (`pc`).
- Memória linear, nas versões que a suportam.
- Execução sequencial das instruções.

Entre as instruções disponíveis estão `add`, `addi`, `mul`, `sub`, `xor`, `xori`, `div`, `slt`, `slti`, `beq`, `jal`, `jalr`, `sw` e `lw`, dependendo da etapa.

### Geração de código

Os visitantes de geração de código percorrem a AST e produzem instruções para a máquina abstrata. Nas etapas `vpl12` a `vpl15`, o driver normalmente executa as fases nesta ordem:

1. Lexer.
2. Parser.
3. Renomeação de variáveis.
4. Geração de instruções.
5. Alocação de registradores, na `vpl15`.
6. Execução do programa.

### Alocação de registradores

`vpl15/Optimizer.py` implementa `RegAllocator`, que utiliza análise de intervalos de vida e uma estratégia de linear scan para mapear variáveis virtuais para os registradores físicos `a0`, `a1`, `a2` e `a3`. Quando os registradores disponíveis não são suficientes, variáveis são derramadas para a memória usando o registrador `sp` como base.

## Decisões e limitações conhecidas

- As etapas são versões didáticas independentes, não um único pacote Python importável pela raiz.
- Não existe uma suíte de testes separada; os testes estão principalmente nos doctests dos próprios módulos.
- O formato da linguagem muda conforme a etapa. Um programa aceito por uma `vpl` inicial pode não ser aceito por uma etapa posterior, e vice-versa.
- Os drivers foram projetados para receber programas pela entrada padrão e alguns comentários indicam que eles fazem parte do material de avaliação das atividades.
- A divisão inteira usa a operação `//` do Python nas implementações avaliadoras e na máquina abstrata.

## Referência rápida

| Etapa | Foco principal |
|---|---|
| `vpl1` | Análise léxica |
| `vpl2` | Expressões e avaliação |
| `vpl3` | Parser de expressões |
| `vpl4` | Variáveis e `let` |
| `vpl5` | Visitors e análise semântica |
| `vpl6` | Verificação de tipos |
| `vpl7` | Geração de restrições |
| `vpl8` | Funções e aplicação |
| `vpl9` | Avaliação funcional e tipos |
| `vpl10` | Parser funcional tipado |
| `vpl11` | Máquina abstrata |
| `vpl12` | Renomeação e geração de código |
| `vpl13` | Compilação para instruções |
| `vpl14` | Memória e controle de fluxo |
| `vpl15` | Otimização e alocação de registradores |

## Autor

Repositório mantido por [HaniBR01](https://github.com/HaniBR01).
