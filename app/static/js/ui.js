// =================================================================================================
//                                      FUNÇÕES DE GESTÃO DA INTERFACE (UI)
// =================================================================================================

/**
 * Reseta a interface para o estado inicial.
 */
function resetarUI() {
    hide(document.getElementById("selectContainer"));
    hide(document.getElementById("btnAnaliseContainer"));
    hide(document.getElementById("abasContainer"));
    hide(document.getElementById("btnSalvarEtapa"));

    document.getElementById("tabelaPerigos").innerHTML = "";
    document.getElementById("inputEtapa").value = "";
    document.getElementById("selectEtapas").innerHTML = "";

    etapaSelecionada = "";
    perigosOrganizados = {};
}

/**
 * Carrega e popula o <select> de produtos agrupados por grupo e subgrupo.
 *
 * @param {object} options - Opções de carregamento.
 * @param {boolean} [options.somenteVetorizados=true] - Se deve carregar apenas produtos com vetores.
 * @param {boolean} [options.habilitarNaoVetorizados=false] - Se deve habilitar produtos sem vetores.
 */
async function carregarProdutosAgrupados({
                                             somenteVetorizados = true, habilitarNaoVetorizados = false
                                         } = {}) {
    const sel = document.getElementById("selectProduto");
    if (!sel) {
        console.warn("#selectProduto não encontrado");
        return;
    }

    // Define o placeholder inicial e desabilita o select
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "-- Carregando produtos... --";
    sel.replaceChildren(placeholder);
    sel.disabled = true;

    try {
        const resp = await fetch(`/crud/produtos/agrupados?somente_vetorizados=${somenteVetorizados ? "true" : "false"}`);
        if (!resp.ok) throw new Error("Falha ao carregar produtos agrupados");
        const data = await resp.json();

        // Ativa o select e define o placeholder final
        sel.disabled = false;
        placeholder.textContent = "-- Escolha um produto --";
        const frag = document.createDocumentFragment();
        frag.appendChild(placeholder);

        // Popula o select com optgroups e options
        for (const g of (data.grupos || [])) {
            for (const sg of (g.subgrupos || [])) {
                const og = document.createElement("optgroup");
                og.label = `${g.grupo} — ${sg.subgrupo}`;

                for (const p of (sg.produtos || [])) {
                    const opt = document.createElement("option");
                    opt.value = p.slug;
                    opt.textContent = p.nome;
                    if (!p.vetorizado && !habilitarNaoVetorizados) {
                        opt.disabled = true;
                        opt.textContent += " (sem índice)";
                    }
                    og.appendChild(opt);
                }
                if (og.children.length) frag.appendChild(og);
            }
        }
        sel.replaceChildren(frag);

        // Oculta o contêiner de consulta até que um produto seja selecionado
        hide(document.getElementById("consultaEtapaContainer"));

    } catch (err) {
        console.error(err);
        sel.replaceChildren(placeholder);
        placeholder.textContent = "Erro ao carregar produtos";
        hide(document.getElementById("consultaEtapaContainer"));
        // Mantém o select desabilitado em caso de erro
        sel.disabled = true;
    }
}

/**
 * Reage à mudança do produto.
 */
function atualizarProduto() {
    produtoSelecionado = document.getElementById("selectProduto").value;
    const container = document.getElementById("consultaEtapaContainer");

    if (produtoSelecionado) {
        show(container);
    } else {
        hide(container);
    }
    resetarUI();
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