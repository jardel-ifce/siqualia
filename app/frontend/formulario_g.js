let produtoSelecionado = "";
let etapaConfirmada = "";
let perigosContexto = [];

// Carrega os produtos no início
document.addEventListener("DOMContentLoaded", async () => {
    const select = document.getElementById("produto");
    try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/produtos");
        const data = await res.json();
        select.innerHTML = '<option value="">Selecione um produto</option>';
        data.forEach(p => {
            const option = document.createElement("option");
            option.value = p.nome_produto;
            option.textContent = p.nome_produto;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Erro ao carregar produtos:", err);
        select.innerHTML = '<option value="">Erro ao carregar produtos</option>';
    } finally {
        setLoading(false);
    }
});

function setLoading(visivel) {
    document.getElementById("loading").style.display = visivel ? "block" : "none";
}

function confirmarProduto() {
    produtoSelecionado = document.getElementById("produto").value;
    etapaConfirmada = "";
    perigosContexto = [];
    document.getElementById("formularioG").style.display = "none";
    document.getElementById("perigosContainer").style.display = "none";
    document.getElementById("confirmacaoEtapa").style.display = "none";
    if (!produtoSelecionado) alert("Selecione um produto.");
}

async function verificarEtapa() {
    const etapaDigitada = document.getElementById("etapa").value.trim();
    if (!produtoSelecionado || !etapaDigitada) {
        alert("Selecione um produto e digite uma etapa.");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/etapa-rag-verificar", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({produto: produtoSelecionado, etapa: etapaDigitada})
        });
        const data = await res.json();
        document.getElementById("etapaSugerida").textContent = data.etapa_sugerida;
        etapaConfirmada = data.etapa_sugerida;
        document.getElementById("confirmacaoEtapa").style.display = "block";
    } catch (err) {
        alert("Erro ao verificar etapa.");
        console.error(err);
    }
}

async function confirmarEtapa() {
    try {
        const res = await fetch("http://127.0.0.1:8000/etapa-rag-perigos", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({produto: produtoSelecionado, etapa: etapaConfirmada})
        });

        const data = await res.json();
        perigosContexto = data.perigos || [];

        const select = document.getElementById("perigo");
        select.innerHTML = '<option value="">Selecione um perigo</option>';

        const grupos = {};
        perigosContexto.forEach((p, idx) => {
            if (!grupos[p.tipo]) grupos[p.tipo] = [];
            grupos[p.tipo].push({...p, idx});
        });

        Object.keys(grupos).forEach(tipo => {
            const optgroup = document.createElement("optgroup");
            optgroup.label = tipo;
            grupos[tipo].forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.idx;
                opt.textContent = p.perigo;
                optgroup.appendChild(opt);
            });
            select.appendChild(optgroup);
        });

        document.getElementById("confirmacaoEtapa").style.display = "none";
        document.getElementById("perigosContainer").style.display = "block";
        document.getElementById("formularioG").style.display = "none";
    } catch (err) {
        alert("Erro ao buscar perigos.");
        console.error(err);
    }
}

async function exibirDetalhesPerigo() {
    const idx = document.getElementById("perigo").value;
    if (idx === "") return;

    const dados = perigosContexto[parseInt(idx)];

    // Mostra dados inicialmente
    document.getElementById("justificativa").innerHTML = dados.justificativa;
    document.getElementById("probabilidade").innerHTML = dados.probabilidade;
    document.getElementById("severidade").innerHTML = dados.severidade;
    document.getElementById("risco").innerHTML = dados.risco;
    document.getElementById("medida").innerHTML = dados.medida_preventiva;
    document.getElementById("perigo_significativo").innerHTML = dados.perigo_significativo;

    try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/formulario/checar-ids", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                produto: produtoSelecionado,
                etapa: etapaConfirmada,
                tipo_perigo: dados.tipo,
                perigo: dados.perigo,
                justificativa: dados.justificativa,
                medida_preventiva: dados.medida_preventiva
            })
        });

        const result = await res.json();
        const icon = (e) =>
            e.existente
                ? '<i class="bi bi-check-circle-fill text-success ms-2"></i>'
                : '<i class="bi bi-plus-circle-fill text-warning ms-2"></i>';

        document.getElementById("justificativa").innerHTML += icon(result.justificativa);
        document.getElementById("medida").innerHTML += icon(result.medida);
        document.getElementById("perigo_significativo").innerHTML += icon(result.perigo);
        document.getElementById("risco").innerHTML += icon(result.perigo);
        document.getElementById("probabilidade").innerHTML += icon(result.perigo);
        document.getElementById("severidade").innerHTML += icon(result.perigo);

    } catch (err) {
        console.error("Erro ao verificar existência dos dados:", err);
    } finally {
        setLoading(false);
        document.getElementById("formularioG").style.display = "block";
    }
}

async function salvarFormularioG() {
    const idx = document.getElementById("perigo").value;
    if (idx === "") {
        alert("Selecione um perigo.");
        return;
    }

    const dados = perigosContexto[parseInt(idx)];

    try {
        setLoading(true);
        const res = await fetch("http://127.0.0.1:8000/formulario-g", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                produto: produtoSelecionado,
                etapa: etapaConfirmada,
                tipo_perigo: dados.tipo,
                perigo: dados.perigo,
                justificativa: dados.justificativa,
                probabilidade: dados.probabilidade,
                severidade: dados.severidade,
                risco: dados.risco,
                medida_preventiva: dados.medida_preventiva,
                perigo_significativo: dados.perigo_significativo
            })
        });

        const data = await res.json();

        if (res.ok) {
            setLoading(false);
            document.getElementById("msgSucesso").textContent = data.message + ` (ID: ${data.id})`;
            document.getElementById("msgSucesso").style.display = "block";
        } else {
            alert("Erro ao salvar: " + data.detail);
        }
    } catch (err) {
        console.error("Erro ao salvar Formulário G:", err);
        alert("Erro na comunicação com o servidor.");
    }
}


