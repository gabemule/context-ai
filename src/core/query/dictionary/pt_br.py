"""
Portuguese (Brazil) programming synonyms and stop words for query expansion.
Common terms used in Brazilian development teams.
"""

# Stop words optimized for Portuguese programming queries
PORTUGUESE_STOP_WORDS = {
    # Artigos (seguros para remover)
    "o", "a", "os", "as", "um", "uma", "uns", "umas",
    
    # Conjunções comuns (geralmente seguros)
    "e", "mas", "porem", "porém", "contudo", "todavia",
    # "ou" removido - importante em programação
    
    # Preposições (dependente do contexto - sendo conservador)
    "de", "da", "do", "das", "dos", "por", "para", "com", "sem",
    # "em", "na", "no" removidos - podem ser importantes
    
    # Pronomes (geralmente seguros para remover)
    "ele", "ela", "eles", "elas", "eu", "tu", "você", "vocês", "nós",
    "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
    
    # Verbos comuns (dependente do contexto - sendo seletivo)
    "são", "era", "eram", "foi", "foram", "será", "serão", "tendo", "tido",
    # "é", "ser", "está", "estar" removidos - podem ser importantes
    
    # Palavras comuns mas geralmente sem importância
    "este", "esta", "estes", "estas", "esse", "essa", "esses", "essas",
    "isto", "isso", "aquilo", "algum", "alguma", "alguns", "algumas",
    "todo", "toda", "todos", "todas", "cada", "muito", "muita", "muitos", "muitas",
    "mais", "menos", "maior", "menor", "outro", "outra", "outros", "outras",
    "mesmo", "mesma", "mesmos", "mesmas", "só", "apenas", "somente", "também",
    "agora", "então", "aqui", "ali", "lá", "onde", "quando", "como", "porque",
    "pode", "podem", "poderia", "poderiam", "deve", "devem", "deveria", "deveriam"
}

# Portuguese programming keywords that should NEVER be stop words
PORTUGUESE_PROGRAMMING_KEYWORDS = {
    # Palavras de pergunta - cruciais para queries de programação
    "como", "que", "qual", "quais", "onde", "quando", "por", "porque", "quem",
    
    # Palavras de ação importantes em programação
    "pegar", "obter", "definir", "usar", "adicionar", "novo", "nova", "velho", "velha",
    "executar", "rodar", "chamar", "fazer", "criar", "buscar", "encontrar", "mostrar", "esconder",
    
    # Palavras de estado/direção importantes em programação
    "cima", "baixo", "dentro", "fora", "ligado", "desligado", "ativo", "inativo",
    
    # Verbos importantes no contexto de programação
    "é", "ser", "está", "estar", "tem", "ter", "vai", "ir", "vem", "vir",
    
    # Preposições importantes no contexto
    "em", "na", "no", "nas", "nos", "ou", "se"
}

# Funções & Métodos
FUNCOES_METODOS = {
    "funcao": ["função", "metodo", "método", "procedimento", "rotina", "function", "method"],
    "função": ["funcao", "metodo", "método", "procedimento", "rotina", "function", "method"],
    "metodo": ["método", "funcao", "função", "procedimento", "rotina", "function", "method"],
    "método": ["metodo", "funcao", "função", "procedimento", "rotina", "function", "method"],
    "procedimento": ["funcao", "função", "metodo", "método", "rotina", "function", "method"],
    "rotina": ["funcao", "função", "metodo", "método", "procedimento", "function", "method"],
}

# Classes & Objetos
CLASSES_OBJETOS = {
    "classe": ["class", "objeto", "tipo", "entidade", "modelo"],
    "objeto": ["object", "classe", "instancia", "instância", "entidade", "item"],
    "instancia": ["instance", "objeto", "classe", "item"],
    "instância": ["instance", "objeto", "classe", "item"],
    "tipo": ["type", "classe", "objeto", "estrutura"],
    "entidade": ["entity", "classe", "objeto", "modelo"],
    "modelo": ["model", "classe", "objeto", "entidade", "schema"],
}

# Variáveis & Dados
VARIAVEIS_DADOS = {
    "variavel": ["variável", "var", "campo", "propriedade", "atributo", "dados"],
    "variável": ["variavel", "var", "campo", "propriedade", "atributo", "dados"],
    "campo": ["field", "propriedade", "atributo", "variavel", "variável", "coluna"],
    "propriedade": ["property", "campo", "atributo", "variavel", "variável"],
    "atributo": ["attribute", "propriedade", "campo", "variavel", "variável"],
    "parametro": ["parâmetro", "param", "argumento", "entrada", "parameter"],
    "parâmetro": ["parametro", "param", "argumento", "entrada", "parameter"],
    "argumento": ["argument", "parametro", "parâmetro", "param", "entrada"],
    "dados": ["data", "informacao", "informação", "conteudo", "conteúdo"],
    "informacao": ["informação", "dados", "data", "conteudo", "conteúdo"],
    "informação": ["informacao", "dados", "data", "conteudo", "conteúdo"],
}

# Componentes UI
COMPONENTES_UI = {
    "componente": ["component", "elemento", "widget", "controle", "parte"],
    "elemento": ["element", "componente", "widget", "controle", "item"],
    "botao": ["botão", "button", "btn", "clique", "acao", "ação"],
    "botão": ["botao", "button", "btn", "clique", "acao", "ação"],
    "entrada": ["input", "campo", "caixa de texto", "formulario", "formulário"],
    "formulario": ["formulário", "form", "entrada", "dialog", "modal"],
    "formulário": ["formulario", "form", "entrada", "dialog", "modal"],
    "tela": ["screen", "pagina", "página", "view", "interface"],
    "pagina": ["página", "page", "tela", "view", "interface"],
    "página": ["pagina", "page", "tela", "view", "interface"],
}

# API & Serviços
API_SERVICOS = {
    "api": ["endpoint", "servico", "serviço", "interface", "rota", "recurso"],
    "servico": ["serviço", "service", "api", "endpoint", "provedor"],
    "serviço": ["servico", "service", "api", "endpoint", "provedor"],
    "rota": ["route", "caminho", "path", "endpoint", "url"],
    "caminho": ["path", "rota", "route", "url", "endereco", "endereço"],
    "requisicao": ["requisição", "request", "chamada", "pedido"],
    "requisição": ["requisicao", "request", "chamada", "pedido"],
    "resposta": ["response", "retorno", "resultado", "saida", "saída"],
    "retorno": ["return", "resposta", "resultado", "saida", "saída"],
    "resultado": ["result", "resposta", "retorno", "saida", "saída"],
}

# Tratamento de Erros
TRATAMENTO_ERROS = {
    "erro": ["error", "excecao", "exceção", "problema", "falha", "bug"],
    "excecao": ["exceção", "exception", "erro", "problema", "falha"],
    "exceção": ["excecao", "exception", "erro", "problema", "falha"],
    "problema": ["problem", "erro", "issue", "falha", "defeito"],
    "falha": ["failure", "erro", "problema", "defeito", "bug"],
    "bug": ["erro", "problema", "falha", "defeito", "issue"],
    "validacao": ["validação", "validation", "verificacao", "verificação", "checagem"],
    "validação": ["validacao", "validation", "verificacao", "verificação", "checagem"],
    "verificacao": ["verificação", "validation", "validacao", "validação", "check"],
    "verificação": ["verificacao", "validation", "validacao", "validação", "check"],
}

# Configuração & Definições
CONFIG_DEFINICOES = {
    "config": ["configuracao", "configuração", "definicoes", "definições", "opcoes", "opções"],
    "configuracao": ["configuração", "config", "definicoes", "definições", "opcoes"],
    "configuração": ["configuracao", "config", "definicoes", "definições", "opcoes"],
    "definicoes": ["definições", "settings", "configuracao", "configuração", "opcoes"],
    "definições": ["definicoes", "settings", "configuracao", "configuração", "opcoes"],
    "opcoes": ["opções", "options", "configuracao", "configuração", "escolhas"],
    "opções": ["opcoes", "options", "configuracao", "configuração", "escolhas"],
    "ambiente": ["environment", "env", "configuracao", "configuração", "setup"],
}

# Autenticação & Segurança
AUTH_SEGURANCA = {
    "auth": ["autenticacao", "autenticação", "login", "seguranca", "segurança"],
    "autenticacao": ["autenticação", "auth", "login", "verificacao", "verificação"],
    "autenticação": ["autenticacao", "auth", "login", "verificacao", "verificação"],
    "login": ["entrar", "acesso", "auth", "autenticacao", "autenticação"],
    "entrar": ["login", "signin", "acesso", "auth"],
    "acesso": ["access", "login", "entrar", "permissao", "permissão"],
    "permissao": ["permission", "permissão", "acesso", "autorizacao", "autorização"],
    "permissão": ["permission", "permissao", "acesso", "autorizacao", "autorização"],
    "token": ["jwt", "sessao", "sessão", "credencial", "chave"],
    "sessao": ["session", "sessão", "token", "auth"],
    "sessão": ["session", "sessao", "token", "auth"],
    "usuario": ["usuário", "user", "cliente", "pessoa"],
    "usuário": ["usuario", "user", "cliente", "pessoa"],
}

# Banco de Dados & Armazenamento
BANCO_ARMAZENAMENTO = {
    "bd": ["db", "banco", "database", "armazenamento", "repositorio", "repositório"],
    "banco": ["database", "bd", "db", "armazenamento", "repositorio", "repositório"],
    "consulta": ["query", "busca", "pesquisa", "select", "sql"],
    "busca": ["search", "consulta", "pesquisa", "find", "query"],
    "pesquisa": ["search", "busca", "consulta", "find", "query"],
    "tabela": ["table", "colecao", "coleção", "entidade", "modelo"],
    "colecao": ["collection", "coleção", "tabela", "lista", "array"],
    "coleção": ["collection", "colecao", "tabela", "lista", "array"],
    "repositorio": ["repository", "repositório", "repo", "armazenamento", "dados"],
    "repositório": ["repository", "repositorio", "repo", "armazenamento", "dados"],
    "armazenamento": ["storage", "banco", "repositorio", "repositório", "dados"],
}

# Testes
TESTES = {
    "teste": ["test", "spec", "verificacao", "verificação", "checagem"],
    "mock": ["simulacao", "simulação", "falso", "stub", "fake"],
    "simulacao": ["simulation", "simulação", "mock", "fake", "stub"],
    "simulação": ["simulation", "simulacao", "mock", "fake", "stub"],
    "verificacao": ["verification", "verificação", "teste", "checagem", "validacao"],
    "verificação": ["verification", "verificacao", "teste", "checagem", "validacao"],
}

# Arquitetura & Padrões
ARQUITETURA_PADROES = {
    "padrao": ["padrão", "pattern", "arquitetura", "estrutura", "abordagem"],
    "padrão": ["padrao", "pattern", "arquitetura", "estrutura", "abordagem"],
    "arquitetura": ["architecture", "estrutura", "design", "padrao", "padrão"],
    "estrutura": ["structure", "arquitetura", "organizacao", "organização", "design"],
    "framework": ["biblioteca", "plataforma", "base", "fundacao", "fundação"],
    "biblioteca": ["library", "lib", "framework", "pacote", "modulo", "módulo"],
    "pacote": ["package", "biblioteca", "modulo", "módulo", "library"],
    "modulo": ["module", "módulo", "pacote", "biblioteca", "componente"],
    "módulo": ["module", "modulo", "pacote", "biblioteca", "componente"],
}

# Desenvolvimento & Processo
DESENVOLVIMENTO_PROCESSO = {
    "deploy": ["publicar", "enviar", "subir", "deployment", "release"],
    "publicar": ["publish", "deploy", "enviar", "subir", "release"],
    "enviar": ["send", "deploy", "publicar", "subir", "push"],
    "subir": ["upload", "deploy", "enviar", "publicar", "push"],
    "build": ["construir", "compilar", "gerar", "criar", "montar"],
    "construir": ["build", "compilar", "gerar", "criar", "montar"],
    "compilar": ["compile", "build", "construir", "gerar", "processar"],
    "gerar": ["generate", "criar", "build", "construir", "produzir"],
    "criar": ["create", "gerar", "build", "construir", "fazer"],
    "debug": ["depurar", "debugar", "investigar", "rastrear", "analisar"],
    "depurar": ["debug", "debugar", "investigar", "rastrear", "analisar"],
    "debugar": ["debug", "depurar", "investigar", "rastrear", "analisar"],
}

# Utilitários & Helpers
UTILITARIOS_HELPERS = {
    "utils": ["utilitarios", "utilitários", "helpers", "ajudantes", "ferramentas"],
    "utilitarios": ["utilitários", "utils", "helpers", "ajudantes", "ferramentas"],
    "utilitários": ["utilitarios", "utils", "helpers", "ajudantes", "ferramentas"],
    "helpers": ["ajudantes", "utilitarios", "utilitários", "utils", "auxiliares"],
    "ajudantes": ["helpers", "utilitarios", "utilitários", "auxiliares", "utils"],
    "auxiliares": ["helpers", "ajudantes", "utilitarios", "utilitários", "utils"],
    "constantes": ["constants", "const", "fixos", "estaticos", "estáticos"],
    "tipos": ["types", "interfaces", "definicoes", "definições", "schemas"],
}

# Combine all categories
PORTUGUESE_SYNONYMS = {}
for category in [
    FUNCOES_METODOS, CLASSES_OBJETOS, VARIAVEIS_DADOS, COMPONENTES_UI,
    API_SERVICOS, TRATAMENTO_ERROS, CONFIG_DEFINICOES, AUTH_SEGURANCA,
    BANCO_ARMAZENAMENTO, TESTES, ARQUITETURA_PADROES, DESENVOLVIMENTO_PROCESSO,
    UTILITARIOS_HELPERS
]:
    PORTUGUESE_SYNONYMS.update(category)