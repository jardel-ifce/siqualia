async function carregarProdutos() {
	const resposta = await fetch("/v1/produtos");
	const produtos = await resposta.json();

	const select = document.getElementById("produtoSelect");
	select.innerHTML = "<option value=''>Selecione...</option>";

	produtos.forEach(produto => {
		const option = document.createElement("option");
		option.value = produto;
		option.textContent = produto.charAt(0).toUpperCase() + produto.slice(1);
		select.appendChild(option);
	});
}

function mostrarCampoEtapa() {
	const produto = document.getElementById("produtoSelect").value;
	const etapaInput = document.getElementById("campoEtapa");
	const selecaoEtapa = document.getElementById("campoSelecaoEtapa");
	const resultadoPerigos = document.getElementById("resultadoPerigos");

	if (produto) {
		etapaInput.style.display = "block";
		selecaoEtapa.style.display = "none";
		resultadoPerigos.innerHTML = "";
	} else {
		etapaInput.style.display = "none";
		selecaoEtapa.style.display = "none";
		resultadoPerigos.innerHTML = "";
	}

	document.getElementById("etapaInput").value = "";
	document.getElementById("etapaSelect").innerHTML = "";
	document.getElementById("salvarContainer").style.display = "none";
}

async function buscarEtapas() {
	const produto = document.getElementById("produtoSelect").value;
	const etapa = document.getElementById("etapaInput").value;
	const resultadoPerigos = document.getElementById("resultadoPerigos");

	resultadoPerigos.innerHTML = "";
	document.getElementById("campoSelecaoEtapa").style.display = "none";
	document.getElementById("salvarContainer").style.display = "none";

	if (!produto || !etapa) {
		alert("Selecione o produto e digite a etapa.");
		return;
	}

	const resposta = await fetch("/v1/etapas/similar", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({produto, etapa})
	});

	const etapas = await resposta.json();
	const select = document.getElementById("etapaSelect");
	select.innerHTML = "";

	etapas.forEach((item) => {
		const option = document.createElement("option");
		option.value = item.etapa;
		option.textContent = `${item.etapa} (origem: ${item.origem}, score: ${item.similaridade})`;
		select.appendChild(option);
	});

	if (etapas.length > 0) {
		document.getElementById("campoSelecaoEtapa").style.display = "block";
	}
}

async function buscarPerigos() {
	const produto = document.getElementById("produtoSelect").value;
	const etapa = document.getElementById("etapaSelect").value;
	const container = document.getElementById("resultadoPerigos");

	container.innerHTML = "";
	document.getElementById("salvarContainer").style.display = "none";

	if (!produto || !etapa) {
		alert("Selecione uma etapa válida para consultar os perigos.");
		return;
	}

	const resposta = await fetch(`/v1/avaliacao?produto=${encodeURIComponent(produto)}&etapa=${encodeURIComponent(etapa)}`);
	const dados = await resposta.json();

	container.innerHTML = `<h3>Formulário G – Etapa: <em>${etapa}</em></h3>`;

	dados.formulario_g.forEach((perigo, index) => {
		const div = document.createElement("div");
		div.className = "perigo-card";
		div.innerHTML = `
      <form id="formulario-${index}">
        ${criarSelect("Tipo de perigo", perigo.tipo, "tipo", ["B", "Q", "F", "A", "QUAL"])}
        ${criarCampo("Descrição do perigo", perigo.perigo, "perigo")}
        ${criarTextarea("Justificativa", perigo.justificativa, "justificativa")}
        ${criarSelect("Probabilidade", perigo.probabilidade, "probabilidade", ["", "Alta", "Média", "Baixa", "Desprezível"])}
        ${criarSelect("Severidade", perigo.severidade, "severidade", ["", "Alta", "Média", "Baixa", "Desprezível"])}
        ${criarSelect("Risco", perigo.risco, "risco", ["", "Alto", "Médio", "Baixo", "Desprezível"])}
        ${criarTextarea("Medida de controle", perigo.medida, "medida")}
        ${criarSelect("Perigo significativo", perigo.perigo_significativo, "perigo_significativo", ["", "Sim", "Não"])}
        <input type="hidden" name="origem" value="${perigo.origem || ''}">
      </form>
      <details class="formulario-h" style="margin-top: 1rem;">
        <summary>Preencher Análise de PCC</summary>
        <div class="form-group">
          <label>1. Existem medidas preventivas?</label>
          <select name="questao_1" onchange="atualizarFluxoH(this)">
            <option value="">Selecione</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>
        <div class="form-group" data-q="q1a" style="display: none;">
          <label>1a. O controle desta fase é necessário à segurança?</label>
          <select name="questao_1a" onchange="atualizarFluxoH(this)">
            <option value="">Selecione</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>
        <div class="form-group" data-q="q2" style="display: none;">
          <label>2. A fase foi desenvolvida para eliminar ou reduzir o perigo?</label>
          <select name="questao_2" onchange="atualizarFluxoH(this)">
            <option value="">Selecione</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>
        <div class="form-group" data-q="q3" style="display: none;">
          <label>3. O perigo pode ocorrer em níveis inaceitáveis?</label>
          <select name="questao_3" onchange="atualizarFluxoH(this)">
            <option value="">Selecione</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>
        <div class="form-group" data-q="q4" style="display: none;">
          <label>4. Existe etapa posterior que possa eliminar ou reduzir?</label>
          <select name="questao_4" onchange="atualizarFluxoH(this)">
            <option value="">Selecione</option>
            <option value="Sim">Sim</option>
            <option value="Não">Não</option>
          </select>
        </div>
        <div class="form-group">
          <label>Resultado:</label>
          <input type="text" name="resultado" readonly />
        </div>
      </details>
    `;
		container.appendChild(div);
	});
	document.getElementById("salvarContainer").style.display = "block";
}

function criarCampo(label, value, name, tipo = "text") {
	return `
    <div class="form-group">
      <label>${label}</label>
      <input type="${tipo}" name="${name}" value="${value || ''}" />
    </div>`;
}

function criarSelect(label, value, name, opcoes) {
	const padrao = (typeof value === "string" && value.trim() !== "" && opcoes.includes(value)) ? value : "";
	const options = opcoes.map(op => `<option value="${op}" ${op === padrao ? "selected" : ""}>${op}</option>`).join("");
	return `
    <div class="form-group">
      <label>${label}</label>
      <select name="${name}">${options}</select>
    </div>`;
}

function criarTextarea(label, value, name) {
	return `
    <div class="form-group">
      <label>${label}</label>
      <textarea name="${name}" rows="2">${value || ''}</textarea>
    </div>`;
}

function atualizarFluxoH(elemento) {
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

async function enviarAvaliacao() {
	const produto = document.getElementById("produtoSelect").value;
	const etapa = document.getElementById("etapaSelect").value;
	const perigoCards = document.querySelectorAll(".perigo-card");
	const formularioG = [];
	const formularioH = [];

	perigoCards.forEach(card => {
		const gData = {};
		const hData = {};
		card.querySelectorAll("form input, form select, form textarea").forEach(el => {
			gData[el.name] = el.value;
		});
		card.querySelectorAll(".formulario-h select, .formulario-h input[name='resultado']").forEach(el => {
			hData[el.name] = el.value;
		});
		formularioG.push(gData);
		formularioH.push(hData);
	});

	const payload = {
		produto,
		etapa,
		formulario_g: formularioG,
		formulario_h: formularioH
	};

	const resposta = await fetch("/v1/avaliacoes/salvar", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify(payload)
	});

	const resultado = await resposta.json();
	alert(resultado.mensagem || "Erro ao salvar.");
}

carregarProdutos();
