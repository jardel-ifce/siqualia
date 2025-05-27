async function carregarProdutos() {
    const resposta = await fetch("/v1/produtos");
    const produtos = await resposta.json();

    const select = document.getElementById("produtoSelect");
    select.innerHTML = "<option value=''>Selecione...</option>";

    produtos.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p.charAt(0).toUpperCase() + p.slice(1);
        select.appendChild(opt);
    });
}

function isFormularioIVazio(formulario_i) {
    if (!formulario_i) return true;

    const camposSimples = [
        formulario_i.limite_critico,
        formulario_i.acao_corretiva,
        formulario_i.registro,
        formulario_i.verificacao
    ];

    const monitoramento = formulario_i.monitoramento || {};
    const camposMonitoramento = [
        monitoramento.oque,
        monitoramento.como,
        monitoramento.quando,
        monitoramento.quem
    ];

    const todosCampos = [...camposSimples, ...camposMonitoramento];
    return todosCampos.every(campo => campo === "");
}

async function carregarEtapas() {
    const produto = document.getElementById("produtoSelect").value;
    if (!produto) {
        alert("Selecione um produto primeiro.");
        return;
    }

    const resposta = await fetch(`/v1/avaliacoes/etapas?produto=${encodeURIComponent(produto)}`);
    const etapas = await resposta.json();
    const tabela = document.getElementById("tabelaResumo");
    const corpo = document.getElementById("corpoTabelaResumo");
    corpo.innerHTML = "";
    tabela.style.display = "table";

    etapas.forEach((registro, i) => {
        const form = registro.formulario_g[0];
        const perigo = registro.resumo[0];
        const formI = perigo.formulario_i;

        const tr = document.createElement("tr");
        const isPCC = perigo.significativo && perigo.resultado === "É um PCC";
        const isFormIPreenchido = !isFormularioIVazio(formI);

        // Botão Formulário I: exibido sempre se for PCC
        const botaoFormI = isPCC ? `
            <button 
                onclick="editarFormI('${registro.produto}', '${registro.etapa}', '${form.tipo}', '${form.perigo}', '${form.justificativa}', '${form.medida}')">
                I
            </button>` : `
            <button disabled title='Apenas para PCCs'>
                I
            </button>`;

        // Botão Relatório: apenas se for PCC e formulário I estiver completo
        const botaoRelatorio = isPCC && isFormIPreenchido ? `
            <button onclick="gerarRelatorio('${registro.arquivo}', 0)">
                Relatório
            </button>` : `
            <button disabled title='Preencha o Formulário I primeiro'>
                Relatório
            </button>`;

        tr.innerHTML = `
        <td>${registro.etapa}</td>
        <td>${perigo.descricao}</td>
        <td>${perigo.resultado || ""}</td>
        <td style="white-space: nowrap;">
          <button onclick="editarFormG('${registro.arquivo}', 0)" title="Formulário G">G</button>
          <button onclick="editarFormH('${registro.arquivo}', 0)" title="Formulário H">H</button>
          ${botaoFormI}
          ${botaoRelatorio}
        </td>
        `;
        corpo.appendChild(tr);
    });
}

function editarFormG(arquivo, indice) {
    alert(`Editar Formulário G para o perigo #${indice + 1} do arquivo:\n${arquivo}`);
}

function editarFormH(arquivo, indice) {
    alert(`Editar Formulário H para o perigo #${indice + 1} do arquivo:\n${arquivo}`);
}

async function editarFormI(produto, etapa, tipo, perigo, justificativa, medida) {
    const url = new URL("/v1/formulario-i/sugerir", window.location.origin);
    url.searchParams.set("produto", produto);
    url.searchParams.set("etapa", etapa);
    url.searchParams.set("tipo", tipo);
    url.searchParams.set("perigo", perigo);
    url.searchParams.set("justificativa", justificativa);
    url.searchParams.set("medida", medida);

    const resp = await fetch(url);
    const dados = await resp.json();

    if (dados.erro) {
        alert(`Erro ao sugerir Formulário I:\n${dados.erro}`);
        return;
    }

    const f = dados.formulario_i;
    const txt = `
	Limite Crítico: ${f.limite_critico}
			
			Monitoramento:
			  - O quê? ${f.monitoramento.oque}
			  - Como? ${f.monitoramento.como}
			  - Quando? ${f.monitoramento.quando}
			  - Quem? ${f.monitoramento.quem}
			
			Ação Corretiva: ${f.acao_corretiva}
			Registro: ${f.registro}
			Verificação: ${f.verificacao}
	`.trim();

    alert(`Sugestão para o Formulário I:\n\n${txt}`);
}

function gerarRelatorio(arquivo, indice) {
    const url = `/relatorio.html?arquivo=${encodeURIComponent(arquivo)}&indice=${indice}`;
    window.open(url, "_blank");
}

let arquivoAtual = "";
let indiceAtual = 0;

async function editarFormI(produto, etapa, tipo, perigo, justificativa, medida) {
    produtoAtual = produto;
    etapaAtual = etapa;
    tipoAtual = tipo;
    perigoAtual = perigo;

    document.getElementById("infoEtapa").textContent = etapa;
    document.getElementById("infoPerigo").textContent = perigo;
    document.getElementById("infoTipo").textContent = tipo;

    const url = new URL("/v1/formulario-i/sugerir", window.location.origin);
    url.searchParams.set("produto", produto);
    url.searchParams.set("etapa", etapa);
    url.searchParams.set("tipo", tipo);
    url.searchParams.set("perigo", perigo);
    url.searchParams.set("justificativa", justificativa);
    url.searchParams.set("medida", medida);

    const resp = await fetch(url);
    const dados = await resp.json();

    if (!dados || !dados.formulario_i) {
        alert("Erro ao carregar sugestões.");
        return;
    }

    const f = dados.formulario_i;
    const form = document.getElementById("formularioIForm");
    form.limite_critico.value = f.limite_critico;
    form["monitoramento.oque"].value = f.monitoramento.oque;
    form["monitoramento.como"].value = f.monitoramento.como;
    form["monitoramento.quando"].value = f.monitoramento.quando;
    form["monitoramento.quem"].value = f.monitoramento.quem;
    form.acao_corretiva.value = f.acao_corretiva;
    form.registro.value = f.registro;
    form.verificacao.value = f.verificacao;

    document.getElementById("modalFormularioI").style.display = "flex";
}


function fecharModal() {
    document.getElementById("modalFormularioI").style.display = "none";
}

let produtoAtual = "";
let etapaAtual = "";
let tipoAtual = "";
let perigoAtual = "";

async function salvarFormularioI() {
    const form = document.getElementById("formularioIForm");

    const dados = {
        produto: produtoAtual,
        etapa: etapaAtual,
        tipo: tipoAtual,
        perigo: perigoAtual,
        formulario_i: {
            limite_critico: form.limite_critico.value,
            monitoramento: {
                oque: form["monitoramento.oque"].value,
                como: form["monitoramento.como"].value,
                quando: form["monitoramento.quando"].value,
                quem: form["monitoramento.quem"].value,
            },
            acao_corretiva: form.acao_corretiva.value,
            registro: form.registro.value,
            verificacao: form.verificacao.value,
        }
    };

    const resp = await fetch("/v1/formulario-i/salvar", {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    const resultado = await resp.json();
    alert(resultado.mensagem || resultado.erro || "Erro ao salvar.");
    fecharModal();
}

carregarProdutos();
