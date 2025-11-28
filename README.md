# LocalVision-Jules

LocalVision-Jules é um assistente de visão local com interface gráfica que permite analisar imagens e manter conversas contextuais usando modelos de linguagem local via LM Studio.

## 📋 Índice

- [Características](#características)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)

## ✨ Características

### Funcionalidades Principais

- **Análise de Imagens**: Descreva imagens detalhadamente usando modelos de visão locais
- **Chat Contextual**: Mantenha conversas com histórico completo
- **Text-to-Speech (TTS)**: Feedback de voz para todas as interações da interface
- **Histórico de Conversas**: Salve e carregue conversas anteriores
- **Drag & Drop**: Arraste imagens diretamente para a interface
- **Colar Imagens**: Cole imagens da área de transferência (Ctrl+V)
- **Bot do Discord**: Integração opcional para analisar imagens em canais do Discord
- **Acessibilidade**: Interface totalmente acessível com suporte a navegação por teclado e feedback de voz

### Recursos de Acessibilidade

- **Ajuste de Fonte**: Aumente ou diminua o tamanho da fonte
- **Temas**: Suporte para tema claro, escuro ou automático
- **TTS Configurável**: Ative ou desative feedback de voz
- **Navegação por Teclado**: Todos os controles acessíveis via teclado
- **Anúncios de Voz**: Botões e campos anunciam seu propósito ao receber foco

## 🏗️ Arquitetura

### Estrutura de Camadas

```
┌─────────────────────────────────────┐
│      Interface Gráfica (UI)         │
│   - CustomTkinter                   │
│   - Drag & Drop (tkinterdnd2)       │
│   - Gerenciamento de Janelas        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Lógica de Negócio           │
│   - LLM Manager                     │
│   - TTS Manager                     │
│   - Image Processor                 │
│   - Discord Bot                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Camada de Dados               │
│   - Database Manager (SQLite)       │
│   - History Manager                 │
└─────────────────────────────────────┘
```

### Componentes Principais

#### UI Layer (`local_vision/ui/`)

- **`main_window.py`**: Interface gráfica principal, janela de configurações e gerenciamento de histórico

#### Logic Layer (`local_vision/logic/`)

- **`llm_manager.py`**: Comunicação com LM Studio via SDK nativo
- **`tts_manager.py`**: Sistema Text-to-Speech com threading e fila de mensagens
- **`image_processor.py`**: Processamento e redimensionamento de imagens
- **`discord_bot.py`**: Bot Discord opcional para processar imagens

#### Data Layer (`local_vision/data/`)

- **`database_manager.py`**: Gerenciamento de conexão e operações SQLite
- **`history_manager.py`**: CRUD de conversas e interações

## 📦 Requisitos

### Software Necessário

1. **Python 3.10+**
2. **LM Studio** instalado e rodando na porta padrão (1234)
3. **Modelo de Visão** carregado no LM Studio (ex: LLaVA, Bakllava)

### Dependências Python

Todas as dependências estão listadas em `requirements.txt`:

- `customtkinter` - Interface gráfica moderna
- `lmstudio` - SDK nativo para comunicação com LM Studio
- `pyttsx3` - Text-to-Speech
- `pillow` - Processamento de imagens
- `tkinterdnd2` - Suporte a drag & drop
- `pyperclipimg` - Colar imagens da área de transferência
- `discord.py` - Integração opcional do Discord

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/LocalVision-Jules.git
cd LocalVision-Jules
```

### 2. Crie um Ambiente Virtual

```bash
python -m venv .venv
```

### 3. Ative o Ambiente Virtual

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 4. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 5. Configure o LM Studio

1. Baixe e instale o [LM Studio](https://lmstudio.ai/)
2. Carregue um modelo de visão (ex: `llava-v1.5-7b`)
3. Inicie o servidor local (porta 1234)

## ⚙️ Configuração

### config.ini

O arquivo `config.ini` é criado automaticamente na primeira execução. Você pode editá-lo manualmente ou através da interface gráfica.

```ini
[Settings]
ModelIdentifier = local-model
DiscordToken =

[Accessibility]
Theme = system
FontSize = 12
VoiceEnabled = True
```

#### Parâmetros de Configuração

- **`ModelIdentifier`**: Identificador do modelo no LM Studio (padrão: `local-model`)
- **`DiscordToken`**: Token do bot do Discord (opcional)
- **`Theme`**: Tema da interface (`light`, `dark`, ou `system`)
- **`FontSize`**: Tamanho da fonte (padrão: 12)
- **`VoiceEnabled`**: Habilitar/desabilitar Text-to-Speech (padrão: True)

### Banco de Dados

O sistema cria automaticamente um arquivo `local_vision.db` (SQLite) com as seguintes tabelas:

- **`conversations`**: Armazena metadados de conversas
- **`interactions`**: Armazena mensagens e imagens de cada conversa

## 🎯 Uso

### Iniciar a Aplicação

#### Windows

```bash
run_app.bat
```

ou manualmente:

```bash
.venv\Scripts\python.exe main.py
```

#### Linux/Mac

```bash
python main.py
```

### Interface Gráfica

#### 1. Tela de Boas-Vindas

Na primeira execução, você será solicitado a inserir um apelido.

#### 2. Janela Principal

##### Enviar Mensagem de Texto

1. Digite sua mensagem no campo de entrada
2. Pressione **Enter** ou clique em **Enviar**

##### Enviar Imagem

**Método 1: Drag & Drop**

- Arraste uma imagem (PNG, JPG, JPEG) para a janela

**Método 2: Botão de Upload**

- Clique no botão **📁** (Upload Image)
- Selecione a imagem

**Método 3: Colar**

- Copie uma imagem para a área de transferência
- Pressione **Ctrl+V** ou clique no botão **📋** (Paste Image)

#### 3. Menu de Configurações

Acesse via botão **⚙️** (Settings):

##### Gerenciar Modelo

- Altere o identificador do modelo LM Studio

##### Acessibilidade

- **Tema**: Escolha entre claro, escuro ou sistema
- **Tamanho da Fonte**: Aumentar (+) ou diminuir (-)
- **Voz**: Habilitar/desabilitar Text-to-Speech

##### Discord Bot (Opcional)

- Cole o token do seu bot Discord
- Clique em **Start Bot** para ativar

#### 4. Histórico de Conversas

Acesse via botão **📜** (History):

- **Carregar Conversa**: Clique duas vezes em uma conversa
- **Excluir Conversa**: Botão de lixeira ao lado da conversa

### Atalhos de Teclado

- **Enter**: Enviar mensagem
- **Ctrl+V**: Colar imagem
- **Tab**: Navegar entre campos
- **Space/Enter** (em botões): Ativar botão

## 🧪 Testes

### Executar Todos os Testes

```bash
python -m unittest discover tests
```

### Executar Testes Específicos

```bash
python -m unittest tests/test_tts.py
python -m unittest tests/test_llm_manager.py
python -m unittest tests/test_database_manager.py
```

### Estrutura de Testes

```
tests/
├── test_tts.py                  # Testes do TTSManager
├── test_llm_manager.py           # Testes do LLM_Manager
├── test_markdown_stripper.py     # Testes de remoção de markdown
├── test_database_manager.py      # Testes do DatabaseManager
├── test_history_manager.py       # Testes do HistoryManager
├── test_image_processor.py       # Testes do ImageProcessor
└── test_discord_bot.py           # Testes do DiscordBot
```

## 📁 Estrutura do Projeto

```
LocalVision-Jules/
├── local_vision/
│   ├── data/
│   │   ├── database_manager.py   # Gerenciamento SQLite
│   │   └── history_manager.py    # CRUD de histórico
│   ├── logic/
│   │   ├── llm_manager.py        # Interface com LM Studio
│   │   ├── tts_manager.py        # Text-to-Speech
│   │   ├── image_processor.py    # Processamento de imagens
│   │   └── discord_bot.py        # Bot Discord
│   └── ui/
│       └── main_window.py        # Interface gráfica
├── tests/
│   ├── test_*.py                 # Testes unitários
├── docs/                         # Documentação adicional
├── main.py                       # Ponto de entrada
├── config.ini                    # Configurações (gerado automaticamente)
├── local_vision.db               # Banco de dados (gerado automaticamente)
├── requirements.txt              # Dependências Python
├── run_app.bat                   # Script de execução (Windows)
└── README.md                     # Este arquivo
```

## 🛠️ Desenvolvimento

### Adicionar Novos Recursos

1. **Crie uma Branch**

   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Implemente o Recurso**

   - Adicione código em `local_vision/`
   - Mantenha a separação de camadas (UI, Logic, Data)

3. **Adicione Testes**

   - Crie testes em `tests/`
   - Garanta cobertura adequada

4. **Execute os Testes**

   ```bash
   python -m unittest discover tests
   ```

5. **Faça Commit e Push**
   ```bash
   git add .
   git commit -m "feat: descrição da funcionalidade"
   git push origin feature/nova-funcionalidade
   ```

### Padrões de Código

- **Sem Comentários Desnecessários**: Use docstrings para documentação
- **Type Hints**: Use anotações de tipo quando apropriado
- **Nomes Descritivos**: Use nomes de variáveis e funções claros
- **Separação de Responsabilidades**: Mantenha as camadas bem definidas

### Debugging

Para habilitar logs detalhados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Adicione testes para novas funcionalidades
4. Envie um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo `LICENSE` para detalhes.

## 🙏 Agradecimentos

- **LM Studio** - Por fornecer uma interface simples para modelos locais
- **CustomTkinter** - Por uma biblioteca moderna de interface gráfica
- **Comunidade Open Source** - Por todas as bibliotecas incríveis utilizadas

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a seção de [Issues](https://github.com/seu-usuario/LocalVision-Jules/issues)
2. Abra uma nova issue se necessário
3. Forneça detalhes sobre o problema (logs, capturas de tela, etc.)

---

**Desenvolvido com ❤️ para facilitar o acesso a modelos de visão local**
