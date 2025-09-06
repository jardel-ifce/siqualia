// app.js

// Importa as funções necessárias de outros módulos
// Assumindo que você está usando módulos ES6 ou que os arquivos são carregados na ordem correta
// No seu caso, com a ordem de scripts no HTML, a importação não é estritamente necessária,
// mas é a melhor prática para uma arquitetura modular.

// Exemplo com import:
// import { carregarProdutosAgrupados } from './ui.js';
// import { hide } from './helpers.js';

// ... e outras funções que precisam ser chamadas

// =================================================================================================
//                                    INICIALIZAÇÃO DA PÁGINA
// =================================================================================================

document.addEventListener("DOMContentLoaded", () => {
    carregarProdutosAgrupados({somenteVetorizados: true});
    hide(document.getElementById("consultaEtapaContainer"));

    // Adicione aqui outros event listeners globais, como para os botões principais
    // document.getElementById("selectProduto").addEventListener("change", atualizarProduto);
    // document.getElementById("consultarEtapa").addEventListener("click", consultarEtapa);
    // ...
});