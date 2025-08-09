// =================================================================================================
//                                    VARIÁVEIS GLOBAIS
// =================================================================================================
let produtoSelecionado = "";
let etapaSelecionada = "";
let perigosOrganizados = {};
let arquivoEtapaSalvo = "";


// =================================================================================================
//                             CONTROLES E INICIALIZAÇÃO DA INTERFACE (UI)
// =================================================================================================

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
 * Carrega a lista de produtos na inicialização da página.
 */
window.onload = async () => {
    const res = await fetch("/crud/produtos");
    const produtos = await res.json();
    const select = document.getElementById("selectProduto");
    produtos.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        select.appendChild(opt);
    });
};

/**
 * Atualiza a interface quando um novo produto é selecionado.
 */
function atualizarProduto() {
    produtoSelecionado = document.getElementById("selectProduto").value;
    document.getElementById("consultaEtapaContainer").style.display = produtoSelecionado ? "block" : "none";
    document.getElementById("selectContainer").style.display = "none";
    document.getElementById("btnAnaliseContainer").style.display = "none";
    document.getElementById("abasContainer").style.display = "none";
    document.getElementById("tabelaPerigos").innerHTML = "";
    document.getElementById("inputEtapa").value = "";
    document.getElementById("selectEtapas").innerHTML = "";
    etapaSelecionada = "";
    perigosOrganizados = {};
}

/**
 * Monta as abas e os formulários de perigo na interface.
 */
function montarAbas() {
    const tipos = ["biologico", "fisico", "quimico", "qualidade", "alergenico"];
    document.querySelectorAll('#abasNav .nav-link').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('#abasConteudo .tab-pane').forEach(pane => pane.classList.remove('active', 'show'));

    tipos.forEach(tipo => {
        const pane = document.getElementById(`tabpane-${tipo}`);
        pane.innerHTML = "";
        const perigos = perigosOrganizados[tipo] || [];

        if (perigos.length > 0) {
            document.getElementById(`tab-${tipo}`).style.display = "";
            const blocoHtml = perigos.map((p, idx) => `
               <div class="border rounded p-3 mb-3" data-perigo-id="${idx}">
               <h3>Análise de Perigos - Formulário G</h3>
                 <h5>Perigo ${idx + 1}</h5>
                    <form class="row g-3" onsubmit="event.preventDefault(); salvarPerigo(this);">
                      <input name="id" type="hidden" value="${p.id || idx}">
                      <div class="col-md-4">
                        <label class="form-label"><strong>Tipo:</strong></label>
                        <select class="form-select" name="tipo">
                          <option${p.tipo === 'B' ? ' selected' : ''}>B</option>
                          <option${p.tipo === 'F' ? ' selected' : ''}>F</option>
                          <option${p.tipo === 'Q' ? ' selected' : ''}>Q</option>
                          <option${p.tipo === 'QUAL' ? ' selected' : ''}>QUAL</option>
                          <option${p.tipo === 'A' ? ' selected' : ''}>A</option>
                        </select>
                      </div>
                      <div class="col-md-8">
                        <label class="form-label"><strong>Perigo:</strong></label>
                        <input class="form-control" name="perigo" type="text" value="${p.perigo}">
                      </div>
                      <div class="col-12">
                        <label class="form-label"><strong>Justificativa:</strong></label>
                        <textarea class="form-control" name="justificativa">${p.justificativa}</textarea>
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><strong>Probabilidade:</strong></label>
                        <select class="form-select" name="probabilidade">
                          ${["Desprezível", "Baixa", "Média", "Alta"].map(op => `
                            <option${p.probabilidade === op ? ' selected' : ''}>${op}</option>`).join("")}
                        </select>
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><strong>Severidade:</strong></label>
                        <select class="form-select" name="severidade">
                          ${["Baixa", "Média", "Alta"].map(op => `
                            <option${p.severidade === op ? ' selected' : ''}>${op}</option>`).join("")}
                        </select>
                      </div>
                      <div class="col-md-4">
                        <label class="form-label"><strong>Risco:</strong></label>
                        <select class="form-select" name="risco">
                          ${["Desprezível", "Baixa", "Média", "Alta"].map(op => `
                            <option${p.risco === op ? ' selected' : ''}>${op}</option>`).join("")}
                        </select>
                      </div>
                      <div class="col-12">
                        <label class="form-label"><strong>Medida:</strong></label>
                        <textarea class="form-control" name="medida">${p.medida}</textarea>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><strong>Perigo Significativo:</strong></label>
                        <select class="form-select" name="perigo_significativo">
                          ${["", "SIM", "NÃO"].map(op => `
                            <option${p.perigo_significativo === op ? ' selected' : ''}>${op}</option>`).join("")}
                        </select>
                      </div>
                      <div class="col-md-6">
                        <label class="form-label"><strong>Origem:</strong></label>
                        <input class="form-control" name="origem" type="text" value="${p.origem}">
                      </div>
                      <div class="col-12 text-end">
                        <button class="btn btn-sm btn-primary" type="submit">Salvar Perigo</button>
                        <button class="btn btn-sm btn-danger" idx idxidxonclick="removerPerigo(idx)"type="button"${idx}>Remover</button>
                      </div>
                    </form>
                 <h3>Determinação PCC - Formulário H</h3>
                 <details class="formulario-h" data-id="${p.id}" style="margin-top: 1rem;">
                   <summary>Preencher Análise de PCC</summary>
                   <hr>
                   <form onsubmit="event.preventDefault(); salvarQuestionario(this)">
                      <div class="form-group mt-2">
                        <label>1. Existem medidas preventivas?</label>
                        <select class="form-select" name="questao_1" onchange="questionario(this)">
                          <option value="">Selecione</option>
                          <option value="Sim">Sim</option>
                          <option value="Não">Não</option>
                        </select>
                      </div>
                      <div class="form-group mt-2" data-q="q1a" style="display: none;">
                        <label>1a. O controle desta fase é necessário à segurança?</label>
                        <select class="form-select" name="questao_1a" onchange="questionario(this)">
                          <option value="">Selecione</option>
                          <option value="Sim">Sim</option>
                          <option value="Não">Não</option>
                        </select>
                      </div>
                      <div class="form-group mt-2" data-q="q2" style="display: none;">
                        <label>2. A fase foi desenvolvida para eliminar ou reduzir o perigo?</label>
                        <select class="form-select" name="questao_2" onchange="questionario(this)">
                          <option value="">Selecione</option>
                          <option value="Sim">Sim</option>
                          <option value="Não">Não</option>
                        </select>
                      </div>
                      <div class="form-group mt-2" data-q="q3" style="display: none;">
                        <label>3. O perigo pode ocorrer em níveis inaceitáveis?</label>
                        <select class="form-select" name="questao_3" onchange="questionario(this)">
                          <option value="">Selecione</option>
                          <option value="Sim">Sim</option>
                          <option value="Não">Não</option>
                        </select>
                      </div>
                      <div class="form-group mt-2" data-q="q4" style="display: none;">
                        <label>4. Existe etapa posterior que possa eliminar ou reduzir?</label>
                        <select class="form-select" name="questao_4" onchange="questionario(this)">
                          <option value="">Selecione</option>
                          <option value="Sim">Sim</option>
                          <option value="Não">Não</option>
                        </select>
                      </div>
                      <div class="form-group mt-2">
                     <label>Resultado:</label>
                       <input class="form-control" name="resultado" readonly type="text">
                     </div>
                   
                     <div class="form-group mt-3 text-end">
                      <button class="btn btn-sm btn-primary" type="submit">Salvar Questionário</button>
                     </div>
                   </form>
                   <hr>
                 </details>
                 
                 <h3 class="mt-4">Resumo do APPCC - Formulário I</h3>
                <details class="formulario-i mt-3">
                  <summary class="mb-2">Preencher Resumo do APPCC</summary>
                  <div class="p-3 border rounded bg-light">
                    
                    <button type="button" class="btn btn-outline-secondary btn-sm mb-3" onclick="sugerirResumo(this)">Sugerir com IA</button>
                
                    <div class="campo-resumo row g-3">
                      <div class="col-12">
                        <label class="form-label">Limite Crítico</label>
                        <textarea class="form-control" name="limite_critico" rows="2"></textarea>
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Monitoramento - O quê?</label>
                        <input class="form-control" name="monitoramento_oque" type="text">
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Monitoramento - Como?</label>
                        <input class="form-control" name="monitoramento_como" type="text">
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Monitoramento - Quando?</label>
                        <input class="form-control" name="monitoramento_quando" type="text">
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Monitoramento - Quem?</label>
                        <input class="form-control" name="monitoramento_quem" type="text">
                      </div>
                
                      <div class="col-12">
                        <label class="form-label">Ação Corretiva</label>
                        <textarea class="form-control" name="acao_corretiva" rows="2"></textarea>
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Registro</label>
                        <input class="form-control" name="registro" type="text">
                      </div>
                
                      <div class="col-md-6">
                        <label class="form-label">Verificação</label>
                        <input class="form-control" name="verificacao" type="text">
                      </div>
                    </div>
                
                    <div class="text-end mt-3">
                      <button type="button" class="btn btn-success btn-sm" onclick="salvarResumo(this)">Salvar Resumo</button>
                    </div>
                  </div>
                </details>

               </div>
             `).join("");

            pane.innerHTML = blocoHtml;
        } else {
            document.getElementById(`tab-${tipo}`).style.display = "none";
        }
    });

    const primeiraAba = tipos.find(tipo => perigosOrganizados[tipo]?.length > 0);
    if (primeiraAba) {
        document.getElementById(`tab-${primeiraAba}`).classList.add("active");
        document.getElementById(`tabpane-${primeiraAba}`).classList.add("active", "show");
    }
}

/**
 * Ativa o comportamento das abas do Bootstrap.
 */
function ativarComportamentoAbas() {
    const tabs = document.querySelectorAll('#abasNav button[data-bs-toggle="tab"]');
    tabs.forEach(triggerEl => {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
}

/**
 * Remove visualmente um perigo da interface.
 * @param {number} idx - O índice do perigo a ser removido.
 */
function removerPerigo(idx) {
    const perigoDiv = document.querySelector(`[data-perigo-id="${idx}"]`);
    if (perigoDiv) perigoDiv.remove();
    console.log("Perigo removido visualmente:", idx);
}


// =================================================================================================
//                             FUNÇÕES DE ANÁLISE E CONSULTA (FLUXO PRINCIPAL)
// =================================================================================================

/**
 * Consulta etapas similares com base em um nome de etapa digitado pelo usuário.
 */
async function consultarEtapa() {
    document.getElementById("selectContainer").style.display = "none";
    document.getElementById("btnAnaliseContainer").style.display = "none";
    document.getElementById("abasContainer").style.display = "none";
    document.getElementById("tabelaPerigos").innerHTML = "";

    const btnSalvar = document.getElementById("btnSalvarEtapa");
    if (btnSalvar) btnSalvar.classList.add("d-none");

    const etapa = document.getElementById("inputEtapa").value.trim();
    etapaSelecionada = etapa;
    if (!etapa) {
        alert("Digite o nome da etapa antes de consultar.");
        return;
    }

    const res = await fetch("/ia/etapas/similar", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({produto: produtoSelecionado, etapa})
    });
    const dados = await res.json();
    const select = document.getElementById("selectEtapas");
    select.innerHTML = "";
    dados.forEach(e => {
        const opt = document.createElement("option");
        opt.value = e.etapa;
        opt.textContent = `${e.etapa} (similaridade: ${e.similaridade})`;
        select.appendChild(opt);
    });
    document.getElementById("selectContainer").style.display = "block";
    await verificarEtapaJaSalva(etapa);
}

/**
 * Busca a etapa selecionada no select e verifica se ela já foi salva.
 */
async function buscarEtapaSelecionada() {
    const etapa = document.getElementById("selectEtapas").value;
    if (!etapa || !produtoSelecionado) return;

    const res = await fetch(`/crud/etapas?produto=${produtoSelecionado}`);
    if (!res.ok) return;

    const etapasSalvas = await res.json();
    const tabela = document.getElementById("tabelaPerigos");
    const btnSalvar = document.getElementById("btnSalvarEtapa");

    const etapaJaSalva = etapasSalvas.includes(etapa);

    if (etapaJaSalva) {
        await verificarEtapaJaSalva(etapa);
        etapaSelecionada = etapa;
        if (btnSalvar) btnSalvar.classList.add("d-none");
    } else {
        alert(`A etapa "${etapa}" não foi encontrada no cadastro. Clique em "Salvar Etapa" para adicioná-la.`);
        if (tabela) tabela.innerHTML = "";
        if (btnSalvar) btnSalvar.classList.remove("d-none");
        document.getElementById("btnAnaliseContainer").style.display = "none";
    }
}

/**
 * Verifica se a etapa já existe no banco de dados e carrega seus dados se ela existir.
 * @param {string} etapaDigitada - O nome da etapa a ser verificada.
 */
async function verificarEtapaJaSalva(etapaDigitada) {
    const res = await fetch(`/crud/etapas?produto=${produtoSelecionado}`);
    if (!res.ok) return;

    const etapasCadastradas = await res.json();
    if (!etapasCadastradas.includes(etapaDigitada)) {
        document.getElementById("tabelaPerigos").innerHTML = "";
        document.getElementById("btnAnaliseContainer").style.display = "none";
        return;
    }

    const etapaSlug = slugify(etapaDigitada);
    const hash = md5(etapaDigitada.trim());
    const nomeArquivo = `${etapaSlug}_${hash}.json`;
    arquivoEtapaSalvo = `avaliacoes/produtos/${produtoSelecionado}/${nomeArquivo}`;

    const timestamp = new Date().getTime();
    const resp = await fetch(`/avaliacoes/produtos/${produtoSelecionado}/${nomeArquivo}?t=${timestamp}`);

    if (!resp.ok) return;

    const etapaJson = await resp.json();
    const perigos = etapaJson.perigos || [];

    if (perigos.length === 0) {
        document.getElementById("tabelaPerigos").innerHTML = `
             <div class="alert alert-warning mt-3">
                Nenhum perigo cadastrado ainda para esta etapa.
             </div>
          `;
    } else {
        const linhas = perigos.map((p, idx) => {
            const perigoItem = p.perigo?.[0] || {};
            const perigoStr = encodeURIComponent(JSON.stringify(p));
            return `
             <tr>
                <td>${etapaJson.etapa}</td>
                <td>${perigoItem.tipo || "-"}</td>
                <td>${perigoItem.perigo || "-"}</td>
                <td>${perigoItem.justificativa || "-"}</td>
                <td>
                   <div class="d-flex">
                      <button class="btn btn-warning btn-sm me-1" title="Formulário G"
                         onclick='abrirModalEditarPerigo(${JSON.stringify(p)}, ${idx}, ${JSON.stringify(etapaJson.etapa)})'>
                         <i class="bi bi-journal-text"></i>
                      </button>
                      <button class="btn btn-sm btn-primary me-1" title="Formulário H"
                         onclick='abrirModalEditarQuestionario(${p.id}, ${JSON.stringify(p.questionario?.[0] || {})})'>
                         <i class="bi bi-journal-richtext"></i>
                      </button>
                      <button class="btn btn-sm btn-success me-1" title="Formulário I"
                        onclick='abrirModalEditarResumo(${JSON.stringify(p)})'>
                        <i class="bi bi-journal-check"></i>
                      </button>
                      <button class="btn btn-sm btn-danger" title="Relatório"
                         onclick="emitirRelatorioPorArquivo('${arquivoEtapaSalvo}', ${p.id})">
                         <i class="bi bi-file-earmark-pdf"></i>
                      </button>
                   </div>
                </td>
             </tr>`;
        }).join("");

        document.getElementById("tabelaPerigos").innerHTML = `
             <table class="table table-bordered table-sm mt-3">
                <thead class="table-light">
                   <tr>
                      <th>Etapa</th>
                      <th>Tipo</th>
                      <th>Perigo</th>
                      <th>Justificativa</th>
                      <th>Ações</th>
                   </tr>
                </thead>
                <tbody>${linhas}</tbody>
             </table>
          `;
    }

    document.getElementById("btnAnaliseContainer").style.display = "block";
}

/**
 * Inicia a análise de perigos sugerindo perigos da IA.
 */
async function iniciarAnalise() {
    const res = await fetch(`/ia/perigos/sugerir?produto=${produtoSelecionado}&etapa=${etapaSelecionada}`);
    const dados = await res.json();
    perigosOrganizados = {};
    const tipoMapeado = {
        "B": "biologico",
        "F": "fisico",
        "Q": "quimico",
        "QUAL": "qualidade",
        "A": "alergenico"
    };

    for (const perigo of dados.formulario_g) {
        const tipo = tipoMapeado[perigo.tipo.toUpperCase()];
        if (!tipo) continue;
        if (!perigosOrganizados[tipo]) perigosOrganizados[tipo] = [];
        perigosOrganizados[tipo].push(perigo);
    }

    montarAbas();
    document.getElementById("abasContainer").style.display = "block";
    ativarComportamentoAbas();
}


// =================================================================================================
//                                      FUNÇÕES DE CRUD
// =================================================================================================

/**
 * Salva uma nova etapa no banco de dados.
 */
async function salvarEtapa() {
    const etapa = document.getElementById("selectEtapas").value;
    const res = await fetch("/crud/etapas/salvar", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({produto: produtoSelecionado, etapa})
    });
    const dados = await res.json();
    etapaSelecionada = etapa;
    arquivoEtapaSalvo = dados.arquivo;
    document.getElementById("btnAnaliseContainer").style.display = "block";
    document.getElementById("btnSalvarEtapa").style.display = "none";
    alert("Etapa salva: " + dados.arquivo);
}

/**
 * Salva um perigo.
 * @param {HTMLFormElement} form - O formulário com os dados do perigo.
 */
async function salvarPerigo(form) {
    const formData = new FormData(form);
    formData.delete('id');
    const data = Object.fromEntries(formData.entries());
    data.produto = produtoSelecionado;
    data.etapa = etapaSelecionada;
    data.arquivo = arquivoEtapaSalvo;

    const resp = await fetch("/crud/perigos/salvar", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    const json = await resp.json();
    if (resp.ok) {
        alert("Perigo salvo com sucesso.");
        const inputId = form.querySelector("input[name='id']");
        if (inputId) inputId.value = json.id;
        const details = form.closest("div").querySelector("details.formulario-h");
        if (details) details.setAttribute("data-id", json.id);
        await verificarEtapaJaSalva(etapaSelecionada);
    } else {
        alert("Erro: " + json.detail);
    }
}

/**
 * Salva as edições de um perigo em um modal.
 */
async function salvarEdicaoPerigo() {
    const form = document.getElementById("formEditarPerigo");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.id = parseInt(data.id);
    data.produto = produtoSelecionado;
    data.arquivo = arquivoEtapaSalvo;

    const response = await fetch("/crud/perigos/atualizar", {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
    });

    const json = await response.json();
    if (response.ok) {
        alert("Perigo atualizado com sucesso.");
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditarPerigo"));
        modal.hide();
        await verificarEtapaJaSalva(data.etapa);
    } else {
        alert("Erro ao atualizar perigo: " + json.detail);
    }
}

/**
 * Salva as respostas de um questionário.
 * @param {HTMLFormElement} form - O formulário com os dados do questionário.
 */
async function salvarQuestionario(form) {
    const perigoId = parseInt(form.closest("details.formulario-h").dataset.id);
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.produto = produtoSelecionado;
    data.etapa = etapaSelecionada;
    data.arquivo = arquivoEtapaSalvo;
    data.id = perigoId;

    const resp = await fetch("/crud/questionario/salvar", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const json = await resp.json();

    if (resp.ok) {
        alert("Questionário salvo com sucesso.");
        await verificarEtapaJaSalva(etapaSelecionada);
    } else {
        alert("Erro: " + json.detail);
    }
}

/**
 * Salva as edições de um questionário em um modal.
 */
async function salvarEdicaoQuestionario() {
    const form = document.getElementById("formEditarQuestionario");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.id = parseInt(data.id);
    data.produto = produtoSelecionado;
    data.etapa = etapaSelecionada;
    data.arquivo = arquivoEtapaSalvo;

    const resp = await fetch("/crud/questionario/salvar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });

    const json = await resp.json();
    if (resp.ok) {
        alert("Questionário salvo com sucesso.");
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditarQuestionario"));
        modal.hide();
        await verificarEtapaJaSalva(data.etapa);
    } else {
        alert("Erro ao salvar questionário: " + json.detail);
    }
}

/**
 * Salva os dados de resumo do APPCC.
 * @param {HTMLElement} botao - O botão que acionou a função.
 */
async function salvarResumo(botao) {
    const bloco = botao.closest("[data-perigo-id]");
    const perigoId = parseInt(bloco.querySelector("input[name='id']").value);
    const dadosResumo = {
        limite_critico: bloco.querySelector("textarea[name='limite_critico']").value,
        monitoramento: {
            oque: bloco.querySelector("input[name='monitoramento_oque']").value,
            como: bloco.querySelector("input[name='monitoramento_como']").value,
            quando: bloco.querySelector("input[name='monitoramento_quando']").value,
            quem: bloco.querySelector("input[name='monitoramento_quem']").value
        },
        acao_corretiva: bloco.querySelector("textarea[name='acao_corretiva']").value,
        registro: bloco.querySelector("input[name='registro']").value,
        verificacao: bloco.querySelector("input[name='verificacao']").value
    };
    const payload = {
        produto: produtoSelecionado,
        etapa: etapaSelecionada,
        id_perigo: perigoId,
        resumo: dadosResumo
    };
    const resp = await fetch("/crud/resumo/salvar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });
    const json = await resp.json();
    if (resp.ok) {
        alert("Resumo salvo com sucesso!");
        await verificarEtapaJaSalva(etapaSelecionada);
    } else {
        alert("Erro ao salvar resumo: " + json.detail);
    }
}

/**
 * Salva as edições de um resumo em um modal.
 */
async function salvarEdicaoResumo() {
    const form = document.getElementById("formEditarResumo");
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    const payload = {
        produto: produtoSelecionado,
        etapa: etapaSelecionada,
        id_perigo: parseInt(data.id),
        limite_critico: data.limite_critico || "",
        monitoramento: {
            oque: data.monitoramento_oque || "",
            como: data.monitoramento_como || "",
            quando: data.monitoramento_quando || "",
            quem: data.monitoramento_quem || "",
        },
        acao_corretiva: data.acao_corretiva || "",
        registro: data.registro || "",
        verificacao: data.verificacao || ""
    };
    const response = await fetch("/crud/resumo/atualizar", {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload),
    });
    const json = await response.json();
    if (response.ok) {
        alert("Resumo atualizado com sucesso.");
        const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditarResumo"));
        modal.hide();
        await verificarEtapaJaSalva(payload.etapa);
    } else {
        alert("Erro ao atualizar o resumo: " + json.detail);
    }
}


// =================================================================================================
//                             FUNÇÕES DE LÓGICA DA INTERFACE (MODAIS)
// =================================================================================================

/**
 * Abre o modal para editar um perigo.
 * @param {object} perigoJson - Os dados do perigo em formato JSON.
 * @param {number} idx - O índice do perigo.
 * @param {string} etapa - O nome da etapa.
 */
function abrirModalEditarPerigo(perigoJson, idx, etapa) {
    const perigoData = typeof perigoJson === "string" ? JSON.parse(perigoJson) : perigoJson;
    const p = perigoData.perigo?.[0] || {};
    const form = document.getElementById("formEditarPerigo");
    form.id.value = perigoData.id || "";
    form.idx.value = idx;
    form.tipo.value = p.tipo || "";
    form.perigo.value = p.perigo || "";
    form.justificativa.value = p.justificativa || "";
    form.probabilidade.value = p.probabilidade || "";
    form.severidade.value = p.severidade || "";
    form.risco.value = p.risco || "";
    form.medida.value = p.medida || "";
    form.perigo_significativo.value = p.perigo_significativo || "";
    form.origem.value = p.origem || "";
    form.arquivo.value = arquivoEtapaSalvo;
    form.produto.value = produtoSelecionado;
    form.etapa.value = etapa || "";
    const modal = new bootstrap.Modal(document.getElementById("modalEditarPerigo"));
    modal.show();
}

/**
 * Abre o modal para editar um questionário.
 * @param {number} perigoId - O ID do perigo.
 * @param {object} questionarioData - Os dados do questionário.
 */
function abrirModalEditarQuestionario(perigoId, questionarioData = {}) {
    const form = document.getElementById("formEditarQuestionario");
    form.reset();
    form.querySelectorAll("[data-q]").forEach(el => el.style.display = "none");
    form.id.value = perigoId;
    form.arquivo.value = arquivoEtapaSalvo;
    form.produto.value = produtoSelecionado;
    form.etapa.value = etapaSelecionada;
    const campos = ["questao_1", "questao_1a", "questao_2", "questao_3", "questao_4"];
    campos.forEach(campo => {
        const el = form.querySelector(`[name='${campo}']`);
        if (el && questionarioData[campo]) {
            el.value = questionarioData[campo];
            el.dispatchEvent(new Event("change"));
        }
    });
    const resultado = form.querySelector("[name='resultado']");
    if (resultado) resultado.value = questionarioData.resultado || "";
    const modal = new bootstrap.Modal(document.getElementById("modalEditarQuestionario"));
    modal.show();
}

/**
 * Abre o modal para editar um resumo, recebendo o objeto completo do perigo.
 * @param {object} perigoObjeto - O objeto completo do perigo.
 */
function abrirModalEditarResumo(perigoObjeto) {
    const form = document.getElementById("formEditarResumo");
    const perigoItem = perigoObjeto.perigo?.[0] || {};

    const modalEl = document.getElementById("modalEditarResumo");

    // Armazena os dados completos do perigo em atributos do modal para a IA usar
    modalEl.setAttribute('data-perigo-tipo', perigoItem.tipo || '');
    modalEl.setAttribute('data-perigo-perigo', perigoItem.perigo || '');
    modalEl.setAttribute('data-perigo-justificativa', perigoItem.justificativa || '');
    modalEl.setAttribute('data-perigo-medida', perigoItem.medida || '');
    modalEl.setAttribute('data-perigo-id', perigoObjeto.id);

    // Preenche os campos do formulário do modal
    form.querySelector("[name='id']").value = perigoObjeto.id;
    form.querySelector("[name='produto']").value = produtoSelecionado;
    form.querySelector("[name='arquivo']").value = arquivoEtapaSalvo;
    form.querySelector("[name='etapa']").value = etapaSelecionada;
    form.querySelector("[name='etapa_visivel']").value = etapaSelecionada;
    form.querySelector("[name='perigo']").value = perigoItem.perigo || "";
    form.querySelector("[name='limite_critico']").value = perigoObjeto.resumo?.[0]?.limite_critico ?? "";
    const mon = perigoObjeto.resumo?.[0]?.monitoramento ?? {};
    form.querySelector("[name='monitoramento_oque']").value = mon.oque ?? "";
    form.querySelector("[name='monitoramento_como']").value = mon.como ?? "";
    form.querySelector("[name='monitoramento_quando']").value = mon.quando ?? "";
    form.querySelector("[name='monitoramento_quem']").value = mon.quem ?? "";
    form.querySelector("[name='acao_corretiva']").value = perigoObjeto.resumo?.[0]?.acao_corretiva ?? "";
    form.querySelector("[name='registro']").value = perigoObjeto.resumo?.[0]?.registro ?? "";
    form.querySelector("[name='verificacao']").value = perigoObjeto.resumo?.[0]?.verificacao ?? "";

    if (modalEl) {
        new bootstrap.Modal(modalEl).show();
    } else {
        console.error("Modal 'modalEditarResumo' não encontrado.");
    }
}

/**
 * Lógica condicional para o questionário em um modal.
 * @param {HTMLElement} elemento - O elemento que acionou a mudança.
 */
function questionarioModal(elemento) {
    const form = elemento.closest("form");
    if (!form) {
        console.error("Formulário da modal não encontrado.");
        return;
    }
    const resultado = form.querySelector("input[name='resultado']");
    if (!resultado) {
        console.error("Campo 'resultado' não encontrado.");
        return;
    }
    const limparAte = {
        "questao_1": ["questao_1a", "questao_2", "questao_3", "questao_4"],
        "questao_1a": [],
        "questao_2": ["questao_3", "questao_4"],
        "questao_3": ["questao_4"],
        "questao_4": []
    };
    const nome = elemento.name;
    const val = elemento.value;
    limparAte[nome].forEach(q => {
        const campo = form.querySelector(`[name='${q}']`);
        if (campo) {
            campo.value = "";
            const grupo = campo.closest(".form-group");
            if (grupo) grupo.style.display = "none";
        }
    });
    resultado.value = "";
    if (nome === "questao_1") {
        if (val === "Não") form.querySelector("[data-q='q1a']").style.display = "block";
        else if (val === "Sim") form.querySelector("[data-q='q2']").style.display = "block";
        return;
    }
    if (nome === "questao_1a") {
        resultado.value = val === "Sim" ? "Modificar o processo" : "Não é um PCC";
        return;
    }
    if (nome === "questao_2") {
        if (val === "Sim") resultado.value = "É um PCC";
        else if (val === "Não") form.querySelector("[data-q='q3']").style.display = "block";
        return;
    }
    if (nome === "questao_3") {
        if (val === "Não") resultado.value = "Não é um PCC";
        else if (val === "Sim") form.querySelector("[data-q='q4']").style.display = "block";
        return;
    }
    if (nome === "questao_4") {
        resultado.value = val === "Sim" ? "Não é um PCC" : "É um PCC";
        return;
    }
}

/**
 * Lógica condicional para o questionário nas abas.
 * @param {HTMLElement} elemento - O elemento que acionou a mudança.
 */
function questionario(elemento) {
    const form = elemento.closest("details.formulario-h");
    const resultado = form.querySelector("input[name='resultado']");
    const limparAte = {
        "questao_1": ["questao_1a", "questao_2", "questao_3", "questao_4"],
        "questao_1a": [],
        "questao_2": ["questao_3", "questao_4"],
        "questao_3": ["questao_4"],
        "questao_4": []
    };
    const nome = elemento.name;
    const val = elemento.value;
    limparAte[nome].forEach(q => {
        const campo = form.querySelector(`[name='${q}']`);
        if (campo) {
            campo.value = "";
            campo.closest(".form-group").style.display = "none";
        }
    });
    resultado.value = "";
    if (nome === "questao_1") {
        if (val === "Não") form.querySelector("[data-q='q1a']").style.display = "block";
        else if (val === "Sim") form.querySelector("[data-q='q2']").style.display = "block";
        return;
    }
    if (nome === "questao_1a") {
        resultado.value = val === "Sim" ? "Modificar o processo" : "Não é um PCC";
        return;
    }
    if (nome === "questao_2") {
        if (val === "Sim") resultado.value = "É um PCC";
        else if (val === "Não") form.querySelector("[data-q='q3']").style.display = "block";
        return;
    }
    if (nome === "questao_3") {
        if (val === "Não") resultado.value = "Não é um PCC";
        else if (val === "Sim") form.querySelector("[data-q='q4']").style.display = "block";
        return;
    }
    if (nome === "questao_4") {
        resultado.value = val === "Sim" ? "Não é um PCC" : "É um PCC";
        return;
    }
}


// =================================================================================================
//                                      FUNÇÕES DE IA
// =================================================================================================

/**
 * Sugere dados de resumo para o APPCC usando a IA.
 * @param {HTMLElement} botao - O botão que acionou a sugestão.
 */
async function sugerirResumo(botao) {
    const bloco = botao.closest("[data-perigo-id]");
    const perigoId = parseInt(bloco.querySelector("input[name='id']").value);
    const tipo = bloco.querySelector("select[name='tipo']").value;
    const perigo = bloco.querySelector("input[name='perigo']").value;
    const justificativa = bloco.querySelector("textarea[name='justificativa']").value;
    const medida = bloco.querySelector("textarea[name='medida']").value;

    const resp = await fetch("/ia/resumo/sugerir", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            produto: produtoSelecionado,
            etapa: etapaSelecionada,
            id_perigo: perigoId,
            tipo,
            perigo,
            justificativa,
            medida
        })
    });
    const json = await resp.json();
    if (!resp.ok) return alert("Erro: " + json.detail);
    const dados = json.resumo;
    bloco.querySelector("textarea[name='limite_critico']").value = dados.limite_critico;
    bloco.querySelector("input[name='monitoramento_oque']").value = dados.monitoramento.oque;
    bloco.querySelector("input[name='monitoramento_como']").value = dados.monitoramento.como;
    bloco.querySelector("input[name='monitoramento_quando']").value = dados.monitoramento.quando;
    bloco.querySelector("input[name='monitoramento_quem']").value = dados.monitoramento.quem;
    bloco.querySelector("textarea[name='acao_corretiva']").value = dados.acao_corretiva;
    bloco.querySelector("input[name='registro']").value = dados.registro;
    bloco.querySelector("input[name='verificacao']").value = dados.verificacao;
}

/**
 * Sugere dados de resumo para o APPCC usando a IA para o formulário no modal de edição.
 */
async function sugerirResumoEdicao() {
    const modalEl = document.getElementById("modalEditarResumo");
    const formResumo = document.getElementById("formEditarResumo");

    // Obtém os dados dos atributos do modal (assumindo que já estão corretos)
    const perigoId = parseInt(modalEl.getAttribute('data-perigo-id'));
    const tipo = modalEl.getAttribute('data-perigo-tipo');
    const perigo = modalEl.getAttribute('data-perigo-perigo');
    const justificativa = modalEl.getAttribute('data-perigo-justificativa');
    const medida = modalEl.getAttribute('data-perigo-medida');

    if (!perigoId || !tipo || !perigo || !justificativa) {
        return alert("Dados do perigo incompletos. Não foi possível sugerir com IA.");
    }

    try {
        const resp = await fetch("/ia/resumo/sugerir", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                produto: produtoSelecionado,
                etapa: etapaSelecionada,
                id_perigo: perigoId,
                tipo,
                perigo,
                justificativa,
                medida
            })
        });

        const json = await resp.json();

        if (!resp.ok) {
            return alert("Erro na sugestão da IA: " + (json.detail || JSON.stringify(json)));
        }

        const dados = json.resumo;
        console.log("Dados da sugestão de IA recebidos:", dados);

        // --- INÍCIO DA LÓGICA DE ATUALIZAÇÃO MAIS SEGURA ---

        // Campos de nível superior
        const limiteCriticoEl = formResumo.querySelector("textarea[name='limite_critico']");
        if (limiteCriticoEl) {
            limiteCriticoEl.value = dados.limite_critico || '';
        } else {
            console.error("Erro: O campo 'limite_critico' não foi encontrado no formulário do modal.");
        }

        const acaoCorretivaEl = formResumo.querySelector("textarea[name='acao_corretiva']");
        if (acaoCorretivaEl) {
            acaoCorretivaEl.value = dados.acao_corretiva || '';
        } else {
            console.error("Erro: O campo 'acao_corretiva' não foi encontrado no formulário do modal.");
        }

        const registroEl = formResumo.querySelector("input[name='registro']");
        if (registroEl) {
            registroEl.value = dados.registro || '';
        } else {
            console.error("Erro: O campo 'registro' não foi encontrado no formulário do modal.");
        }

        const verificacaoEl = formResumo.querySelector("input[name='verificacao']");
        if (verificacaoEl) {
            verificacaoEl.value = dados.verificacao || '';
        } else {
            console.error("Erro: O campo 'verificacao' não foi encontrado no formulário do modal.");
        }

        // Campos do objeto aninhado 'monitoramento'
        const monitoramento = dados.monitoramento || {};
        const oqueEl = formResumo.querySelector("input[name='monitoramento_oque']");
        if (oqueEl) {
            oqueEl.value = monitoramento.oque || '';
        } else {
            console.error("Erro: O campo 'monitoramento_oque' não foi encontrado no formulário do modal.");
        }

        const comoEl = formResumo.querySelector("input[name='monitoramento_como']");
        if (comoEl) {
            comoEl.value = monitoramento.como || '';
        } else {
            console.error("Erro: O campo 'monitoramento_como' não foi encontrado no formulário do modal.");
        }

        const quandoEl = formResumo.querySelector("input[name='monitoramento_quando']");
        if (quandoEl) {
            quandoEl.value = monitoramento.quando || '';
        } else {
            console.error("Erro: O campo 'monitoramento_quando' não foi encontrado no formulário do modal.");
        }

        const quemEl = formResumo.querySelector("input[name='monitoramento_quem']");
        if (quemEl) {
            quemEl.value = monitoramento.quem || '';
        } else {
            console.error("Erro: O campo 'monitoramento_quem' não foi encontrado no formulário do modal.");
        }

        // --- FIM DA LÓGICA DE ATUALIZAÇÃO MAIS SEGURA ---

        alert("Sugestão da IA aplicada com sucesso!");

    } catch (error) {
        console.error("Ocorreu um erro inesperado ao tentar obter ou aplicar a sugestão da IA:", error);
        alert("Ocorreu um erro inesperado. Verifique o console para mais detalhes.");
    }
}

// =================================================================================================
//                                      FUNÇÕES UTILITÁRIAS
// =================================================================================================

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
 * Emite um relatório por índice.
 * @param {string} produto
 * @param {string} etapa
 * @param {number} id_perigo
 */
function emitirRelatorioPorIndice(produto, etapa, id_perigo) {
    const etapaStr = String(etapa || "");
    const hash = md5(etapaStr.trim());
    const etapaFormatada = etapaStr.trim().toLowerCase().replace(/\s+/g, "_").replace(/[^\w_]/g, "");
    const arquivo = `avaliacoes/produtos/${produto}/${etapaFormatada}_${hash}.json`;
    const url = new URL("/static/relatorio.html", window.location.origin);
    url.searchParams.set("arquivo", arquivo);
    url.searchParams.set("indice", id_perigo);
    console.log("Abrindo relatório para:", arquivo, "ID:", id_perigo);
    window.open(url.toString(), "_blank");
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