# 📊 Django Data Management System

Este é um sistema de gerenciamento de dados desenvolvido em Django, que permite a importação, consulta e gerenciamento de dados de clientes e débitos. O sistema inclui funcionalidades para importar dados de arquivos CSV, realizar consultas detalhadas sobre clientes e gerenciar informações relacionadas a débitos.

## 🚀 Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/llongaray/Sistema-de-Consulta-Money.git
   cd Sistema-de-Consulta-Money
   ```

2. **Crie um ambiente virtual e ative-o:**
   ```bash
   python -m venv env
   source env/bin/activate  # Para Windows use `env\Scripts\activate`
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados:**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário para acessar o admin:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

## 📄 Uso

- **Consulta de Cliente:**
  - Acesse `http://127.0.0.1:8000/consulta_cliente` para buscar clientes pelo CPF.
  - Visualize as informações do cliente acessando a URL com o CPF: `http://127.0.0.1:8000/ficha_cliente/<cpf>`.

- **Gerenciamento de Dados:**
  - Acesse `http://127.0.0.1:8000/gerenciamento` para importar dados de um arquivo CSV.
  - Certifique-se de que o CSV contenha as colunas esperadas para uma importação bem-sucedida.

## 🔧 Contribuição

1. Faça um fork do repositório.
2. Crie uma nova branch (`git checkout -b feature-branch`).
3. Faça suas mudanças e adicione commits (`git commit -am 'Adiciona nova feature'`).
4. Envie suas mudanças para o repositório remoto (`git push origin feature-branch`).
5. Abra um pull request.

## 📝 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚙️ Funcionalidades

### Consulta de Cliente

A função de consulta de cliente permite que os usuários busquem clientes pelo CPF. Se o CPF for encontrado no banco de dados, o usuário é redirecionado para a página de detalhes do cliente. Caso contrário, uma mensagem de erro é retornada.

### Importação de Dados CSV

A funcionalidade de importação de dados permite que os usuários carreguem um arquivo CSV contendo dados dos clientes. O sistema então processa este arquivo e importa os dados para o banco de dados, desde que o CSV contenha as colunas esperadas.

### Funções de Usuário

As funções de gerenciamento de usuários incluem login, registro, e logout. O sistema autentica os usuários com base no nome de usuário e senha, permite o registro de novos usuários e gerencia a sessão de login/logout.

### Modelos

#### Cliente

O modelo de Cliente define a estrutura dos dados dos clientes, incluindo campos como nome, CPF, UF, e situação funcional. Cada campo é definido com suas respectivas restrições e tipos de dados.

#### MatriculaDebitos

O modelo MatriculaDebitos define a estrutura dos dados de débitos dos clientes, incluindo informações como matrícula, rubrica, banco, órgão, e valores de débitos e créditos. Este modelo está relacionado ao modelo Cliente, permitindo associar múltiplos débitos a um único cliente.

---

Para mais informações, consulte a [documentação do Django](https://docs.djangoproject.com/en/stable/).
