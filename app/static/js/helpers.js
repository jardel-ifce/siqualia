// =================================================================================================
//                                      FUNÇÕES UTILITÁRIAS E HELPERS
// =================================================================================================

// Helpers de manipulação de classes CSS (Bootstrap)
const show = el => el && el.classList.remove('d-none');
const hide = el => el && el.classList.add('d-none');

/**
 * Exibe uma mensagem de alerta na interface.
 * @param {string} texto - O conteúdo da mensagem.
 * @param {string} tipo - O tipo de alerta (ex: 'success', 'warning', 'danger').
 */
function mostrarMensagem(texto, tipo = "success") {
    const msg = document.getElementById("mensagem");
    msg.innerHTML = `<div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
        ${texto}
        <button aria-label="Close" class="btn-close" data-bs-dismiss="alert" type="button"></button>
        </div>`;
}

/**
 * Limpa a área de mensagens da interface.
 */
function limparMensagem() {
    document.getElementById("mensagem").innerHTML = "";
}

/**
 * Formata uma pontuação para exibição em porcentagem.
 * @param {number} score - A pontuação a ser formatada (de 0 a 1).
 * @returns {string|null} A pontuação formatada ou null se inválida.
 */
function formatScore(score) {
    if (score == null || isNaN(score)) return null;
    const pct = score <= 1 ? score * 100 : score;
    return `${Math.round(Math.max(0, Math.min(pct, 100)))}%`;
}

/**
 * Extrai a pontuação de similaridade de um objeto.
 * @param {object} x - O objeto que contém a pontuação.
 * @returns {number|null} A pontuação bruta ou null se não encontrada.
 */
function extrairScoreBruto(x) {
    if (typeof x?.score === "number") return x.score;
    if (typeof x?.similaridade === "number") return x.similaridade;
    if (typeof x?.similarity === "number") return x.similarity;
    if (typeof x?.distance === "number") return 1 - x.distance;
    if (typeof x?.distancia === "number") return 1 - x.distancia;
    return null;
}

/**
 * Converte uma string em um formato "slug".
 * @param {string} texto - O texto a ser convertido.
 * @returns {string} O texto em formato slug.
 */
function slugify(texto) {
    return texto
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim()
        .replace(/\s+/g, "_")
        .replace(/\//g, "_")
        .replace(/[^\w\-]+/g, "");
}

/**
 * Emite um relatório por arquivo.
 * @param {string} arquivo
 * @param {number} id_perigo
 */
function emitirRelatorioPorArquivo(arquivo, id_perigo) {
    if (!arquivo || typeof id_perigo === "undefined") {
        console.error("Dados inválidos:", {arquivo, id_perigo});
        return;
    }
    const url = new URL("/static/relatorio.html", window.location.origin);
    url.searchParams.set("arquivo", arquivo);
    url.searchParams.set("indice", id_perigo);
    console.log("Abrindo relatório para:", arquivo, "ID:", id_perigo);
    window.open(url.toString(), "_blank");
}