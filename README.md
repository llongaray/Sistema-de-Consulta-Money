# Documentação do Sistema de Ranking e Meta

Este documento fornece uma visão geral das alterações e implementações realizadas no sistema de ranking e meta. O sistema foi desenvolvido para calcular e exibir o ranking dos funcionários com base em metas e valores registrados.

## Sumário

1. [Objetivo](#objetivo)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Atualizações Recentes](#atualizações-recentes)
4. [Integrações e Funcionalidades](#integrações-e-funcionalidades)
5. [Instruções de Uso](#instruções-de-uso)
6. [Conclusão](#conclusão)

## Objetivo

O sistema visa fornecer uma interface para adicionar metas e calcular o ranking dos funcionários com base em seu desempenho em relação às metas estabelecidas. As principais funcionalidades incluem a criação e visualização de metas, cálculo do ranking de funcionários e exibição de progresso em relação às metas.

## Estrutura do Projeto

O projeto é composto por diversas partes principais:

- **Modelos**: Definem a estrutura dos dados, incluindo `RegisterMeta`, `RegisterMoney`, e `Ranking`.
- **Views**: Contêm a lógica de negócios para manipular dados e renderizar páginas.
- **Templates HTML**: São utilizados para criar a interface do usuário e coletar dados dos formulários.
- **JavaScript**: Gerencia a interação dinâmica com a interface e atualiza os dados exibidos.

## Atualizações Recentes

### Atualizações no JavaScript

O script JavaScript foi atualizado para:

- **Formatar Valores**: Adicionar uma função para formatar valores numéricos como `###.###,##`.
- **Renderizar Ranking**: Modificar a função `renderRanking` para exibir os dados de ranking, incluindo valores formatados e porcentagens.
- **Buscar Dados**: Implementar uma função `fetchRankingData` para buscar dados de ranking e atualizar a interface periodicamente.

### Atualizações na View `get_ranking_data`

As seguintes alterações foram feitas na função `get_ranking_data`:

- **Correção na Cálculo do Valor Total**: Atualizar o cálculo do valor total para somar valores individuais dos funcionários.
- **Correção na Cálculo da Porcentagem**: Ajustar o cálculo da porcentagem de progresso do ranking com base no valor somado.
- **Renomeação de Variáveis**: Renomear `valor_total` para `valor_sum_colab` para evitar confusão com `valor_total` de meta.

### Atualizações na View `import_metas`

Foram adicionadas funcionalidades para:

- **Importar Metas**: Adicionar e salvar metas com campos como `titulo`, `valor`, `setor`, `range_data_inicio`, `range_data_final` e `descricao`.
- **Validar Dados**: Verificar e processar os dados do formulário para garantir a integridade antes de salvar.

### Atualizações no HTML

O formulário HTML foi atualizado para incluir um campo adicional para `titulo` na criação de metas.

## Integrações e Funcionalidades

O sistema integra várias funcionalidades para:

- **Adicionar Metas**: Utilizando um formulário HTML para capturar dados e armazenar no banco de dados.
- **Calcular Ranking**: Usar dados registrados para calcular e exibir o ranking dos funcionários.
- **Atualização Dinâmica**: Atualizar periodicamente os dados de ranking e progresso usando JavaScript.

## Instruções de Uso

1. **Adicionar Metas**: Navegue até o formulário de metas e preencha os campos necessários. Submeta o formulário para salvar uma nova meta.
2. **Visualizar Ranking**: O ranking é exibido na interface de usuário e atualizado periodicamente com base nas metas e valores registrados.
3. **Atualizar Dados**: O sistema busca e atualiza dados periodicamente para garantir informações atualizadas.

## Conclusão

Este projeto fornece uma solução completa para gerenciamento e visualização de metas e rankings de funcionários. As atualizações recentes aprimoram a funcionalidade e a clareza do sistema, garantindo que os dados sejam exibidos corretamente e de forma intuitiva.
