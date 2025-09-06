// appcc_teste.js
// Assistente APPCC (Ambiente de Teste)
// Fluxo: Produto → Etapa → Tipo de perigo → Perigo → Justificativa → BPF/Probabilidade → Severidade → Matriz de Risco → Medidas (se preciso) → Significativo → Salvar

// =====================
// Config / util sessão
// =====================
const API = "/api"; // mesma origem do FastAPI
const KEY = `siqualia_appcc_teste_${getSessionId()}`;

function getSessionId() {
  if (!sessionStorage.getItem("sid")) {
    // um id por aba: mantém cache separado
    sessionStorage.setItem("sid", crypto.randomUUID());
  }
  return sessionStorage.getItem("sid");
}

function loadDraft() {
  const s = localStorage.getItem(KEY);
  return s ? JSON.parse(s) : {};
}

function saveDraft(patch) {
  const cur = loadDraft();
  const next = { ...cur, ...patch, updatedAt: new Date().toISOString() };
  localStorage.setItem(KEY, JSON.stringify(next));
  drawStatus();

  // salva também no cache do servidor (debounce simples)
  clearTimeout(saveDraft._t);
  saveDraft._t = setTimeout(() => {
    fetch(`${API}/cache/salvar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId: getSessionId(), state: loadDraft() })
    }).catch(() => {});
  }, 350);

  return next;
}

function drawStatus() {
  const s = loadDraft();
  const el = document.getElementById("statusBar");
  if (!el) return;
  el.textContent = s.updatedAt ? `Rascunho salvo: ${new Date(s.updatedAt).toLocaleString()}` : "Rascunho: —";
}

function goto(step) {
  document.querySelectorAll(".step").forEach(sec => {
    sec.classList.toggle("active", sec.dataset.step === String(step));
  });
}

function back() {
  const s = loadDraft();
  const n = (s._step || 1) - 1;
  if (n >= 1) {
    saveDraft({ _step: n });
    goto(n);
  }
}

// liga todos os botões com data-back
document.querySelectorAll("[data-back]").forEach(b => b.addEventListener("click", back));


// ==================================
// Passo 1 — Seleção inicial (campos)
// ==================================
const produto = document.getElementById("produto");
const etapa = document.getElementById("etapa");
const tipoPerigo = document.getElementById("tipoPerigo");
const perigoDescricao = document.getElementById("perigoDescricao");
const justificativa = document.getElementById("justificativa");
const next1 = document.getElementById("next1");

if (next1) {
  next1.addEventListener("click", () => {
    if (!produto.value || !etapa.value || !tipoPerigo.value || !perigoDescricao.value || !justificativa.value) {
      alert("Preencha todos os campos do Passo 1 antes de continuar.");
      return;
    }
    saveDraft({
      produto: produto.value,
      etapa: etapa.value,
      tipoPerigo: tipoPerigo.value,
      perigoDescricao: perigoDescricao.value,
      justificativa: justificativa.value,
      _step: 2
    });
    goto(2);
  });
}

// autosave do Passo 1
[produto, etapa, tipoPerigo, perigoDescricao, justificativa].forEach(el => {
  if (!el) return;
  el.addEventListener("input", () =>
    saveDraft({
      produto: produto.value,
      etapa: etapa.value,
      tipoPerigo: tipoPerigo.value,
      perigoDescricao: perigoDescricao.value,
      justificativa: justificativa.value
    })
  );
});


// =======================================================
// Passo 2 — Questionário BPF (probabilidade via predição)
// =======================================================
const bpfForm = document.getElementById("bpfForm");
const btnPredizer = document.getElementById("btnPredizer");
const probOut = document.getElementById("probOut");
const next2 = document.getElementById("next2");

function readBPF() {
  const map = {};
  document.querySelectorAll("#bpfForm [data-key]").forEach(el => {
    const key = el.dataset.key;
    // todos os campos são numéricos no modelo (0/1/2 ou number)
    let val = el.value;
    if (el.type === "number") {
      val = Number(val);
    } else {
      // selects com "0/1/2"
      val = Number(val);
    }
    map[key] = val;
  });
  return map;
}

function hydrateBPF(bpf) {
  if (!bpf) return;
  document.querySelectorAll("#bpfForm [data-key]").forEach(el => {
    const key = el.dataset.key;
    if (Object.prototype.hasOwnProperty.call(bpf, key) && bpf[key] !== undefined && bpf[key] !== null) {
      el.value = String(bpf[key]);
    }
  });
}

async function predictProbabilidade(bpfRespostas) {
  const resp = await fetch(`${API}/predicao`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bpfRespostas })
  });
  const data = await resp.json();
  // data.prob_classe: "DESPREZÍVEL|BAIXA|MÉDIA|ALTA"
  // data.prob_score: número 0..1 (opcional)
  return data;
}

if (btnPredizer) {
  btnPredizer.addEventListener("click", async () => {
    const bpfRespostas = readBPF();

    // validação simples
    const t = Number(bpfRespostas["tempo_exposicao_ar"]);
    if (isNaN(t) || t < 5 || t > 60) {
      alert("Tempo de exposição ao ar deve estar entre 5 e 60 minutos.");
      return;
    }

    try {
      const data = await predictProbabilidade(bpfRespostas);
      const prob = data.prob_classe || data.probabilidade || "DESPREZÍVEL";
      const scoreStr = typeof data.prob_score === "number" ? ` (score: ${data.prob_score.toFixed(2)})` : "";
      if (probOut) probOut.textContent = prob + scoreStr;

      saveDraft({ bpfRespostas, probabilidade: prob, prob_score: data.prob_score });
      if (next2) next2.disabled = false;
    } catch (e) {
      console.error("Falha ao calcular probabilidade:", e);
      alert("Não foi possível calcular a probabilidade. Verifique o backend.");
    }
  });
}

// se o usuário editar as respostas BPF após predição, invalidar o resultado e exigir novo cálculo
if (bpfForm) {
  bpfForm.addEventListener("input", () => {
    const updated = readBPF();
    saveDraft({ bpfRespostas: updated, probabilidade: undefined, prob_score: undefined });
    if (probOut) probOut.textContent = "—";
    if (next2) next2.disabled = true;
  });
}

if (next2) {
  next2.addEventListener("click", () => {
    const s = loadDraft();
    if (!s.probabilidade) {
      alert("Calcule a probabilidade antes de prosseguir.");
      return;
    }
    saveDraft({ _step: 3 });
    goto(3);
  });
}


// ============================
// Passo 3 — Severidade (radio)
// ============================
const next3 = document.getElementById("next3");
document.querySelectorAll('input[name="sev"]').forEach(r => {
  r.addEventListener("change", () => {
    if (next3) next3.disabled = false;
  });
});

if (next3) {
  next3.addEventListener("click", async () => {
    const sev = document.querySelector('input[name="sev"]:checked')?.value;
    const prob = loadDraft().probabilidade;
    if (!sev || !prob) {
      alert("Selecione a severidade e calcule a probabilidade.");
      return;
    }
    try {
      const r = await fetch(`${API}/risco`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ probabilidade: prob, severidade: sev })
      });
      const { risco, exige_medidas } = await r.json();
      saveDraft({ severidade: sev, risco, exige_medidas, _step: 4 });
      renderRisco();
      goto(4);
    } catch (e) {
      console.error("Falha ao calcular risco:", e);
      alert("Não foi possível calcular o risco. Verifique o backend.");
    }
  });
}


// ======================================
// Passo 4 — Matriz Risco + Medidas (MP)
// ======================================
const probResumo = document.getElementById("probResumo");
const sevResumo = document.getElementById("sevResumo");
const riscoBadge = document.getElementById("riscoBadge");
const mpExtra = document.getElementById("mp-extra");
const medidasPreventivas = document.getElementById("medidasPreventivas");
const next4 = document.getElementById("next4");

function renderRisco() {
  const s = loadDraft();

  if (probResumo) probResumo.textContent = s.probabilidade || "—";
  if (sevResumo) sevResumo.textContent = s.severidade || "—";

  if (riscoBadge) {
    riscoBadge.textContent = `Risco: ${s.risco || "—"}`;
    riscoBadge.className = "risk-badge";
    if (s.risco === "Alto") riscoBadge.classList.add("risk-alto");
    else if (s.risco === "Médio") riscoBadge.classList.add("risk-medio");
    else if (s.risco === "Baixo") riscoBadge.classList.add("risk-baixo");
    else if (s.risco === "Desprezível") riscoBadge.classList.add("risk-desp");
  }

  const needMP = (typeof s.exige_medidas === "boolean")
    ? s.exige_medidas
    : (s.risco && s.risco !== "Desprezível");

  if (mpExtra) mpExtra.classList.toggle("hidden", !needMP);

  if (next4) {
    if (needMP) {
      next4.disabled = !(s.medidasPreventivas && s.medidasPreventivas.trim());
    } else {
      next4.disabled = false;
    }
  }
}

if (medidasPreventivas) {
  medidasPreventivas.addEventListener("input", (e) => {
    saveDraft({ medidasPreventivas: e.target.value });
    renderRisco();
  });
}

if (next4) {
  next4.addEventListener("click", () => {
    saveDraft({ _step: 5 });
    goto(5);
  });
}


// ========================================
// Passo 5 — Perigo Significativo? (radio)
// ========================================
const next5 = document.getElementById("next5");
document.querySelectorAll('input[name="signif"]').forEach(r => {
  r.addEventListener("change", () => {
    if (next5) next5.disabled = false;
  });
});

if (next5) {
  next5.addEventListener("click", () => {
    const val = document.querySelector('input[name="signif"]:checked')?.value === "true";
    saveDraft({ significativo: val, _step: 6 });
    renderReview();
    goto(6);
  });
}


// =====================================
// Passo 6 — Revisão & salvamento final
// =====================================
const reviewBox = document.getElementById("reviewBox");
const btnSalvar = document.getElementById("btnSalvar");

function renderReview() {
  const s = loadDraft();
  const out = {
    produto: s.produto,
    etapa: s.etapa,
    tipoPerigo: s.tipoPerigo,
    perigoDescricao: s.perigoDescricao,
    justificativa: s.justificativa,
    bpfRespostas: s.bpfRespostas || {},
    probabilidade: s.probabilidade,
    prob_score: s.prob_score,
    severidade: s.severidade,
    risco: s.risco,
    medidasPreventivas: s.medidasPreventivas || "",
    significativo: s.significativo ?? null
  };
  if (reviewBox) reviewBox.textContent = JSON.stringify(out, null, 2);
}

if (btnSalvar) {
  btnSalvar.addEventListener("click", async () => {
    const s = loadDraft();

    // validações finais
    if (!s.produto || !s.etapa || !s.tipoPerigo || !s.perigoDescricao || !s.justificativa) {
      alert("Dados incompletos do Passo 1.");
      return;
    }
    if (!s.bpfRespostas || typeof s.probabilidade !== "string") {
      alert("Calcule a probabilidade (Passo 2).");
      return;
    }
    if (!s.severidade || !s.risco) {
      alert("Defina severidade e risco (Passos 3 e 4).");
      return;
    }
    const needMP = (typeof s.exige_medidas === "boolean")
      ? s.exige_medidas
      : (s.risco && s.risco !== "Desprezível");
    if (needMP && !(s.medidasPreventivas && s.medidasPreventivas.trim())) {
      alert("Informe as medidas preventivas.");
      return;
    }
    if (typeof s.significativo !== "boolean") {
      alert("Responda se o perigo é significativo (Passo 5).");
      return;
    }

    try {
      const resp = await fetch(`${API}/finalizar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId: getSessionId(), registro: s })
      });
      if (!resp.ok) throw new Error("Falha HTTP");
      const data = await resp.json();
      alert(`Registro salvo. Total: ${data.total_registros}\nArquivo: ${data.arquivo}`);

      // reset do rascunho: limpa storage e recarrega
      localStorage.removeItem(KEY);
      // opcional: limpa cache no servidor
      fetch(`${API}/cache/salvar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId: getSessionId(), state: {} })
      }).catch(() => {});
      location.reload();
    } catch (e) {
      console.error("Falha ao salvar:", e);
      alert("Não foi possível salvar. Verifique o backend.");
    }
  });
}


// ==========================
// Botão "Limpar rascunho"
// ==========================
const btnLimpar = document.getElementById("btnLimpar");
if (btnLimpar) {
  btnLimpar.addEventListener("click", async () => {
    localStorage.removeItem(KEY);
    try {
      await fetch(`${API}/cache/salvar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId: getSessionId(), state: {} })
      });
    } catch (_) {}
    location.reload();
  });
}


// ==========================
// Bootstrap inicial da UI
// ==========================
(function init() {
  drawStatus();
  const s = loadDraft();

  // reidrata Passo 1
  if (produto && s.produto) produto.value = s.produto;
  if (etapa && s.etapa) etapa.value = s.etapa;
  if (tipoPerigo && s.tipoPerigo) tipoPerigo.value = s.tipoPerigo;
  if (perigoDescricao && s.perigoDescricao) perigoDescricao.value = s.perigoDescricao;
  if (justificativa && s.justificativa) justificativa.value = s.justificativa;

  // reidrata BPF e estado do Passo 2
  if (s.bpfRespostas) hydrateBPF(s.bpfRespostas);
  if (probOut) {
    if (s.probabilidade) {
      const scoreStr = typeof s.prob_score === "number" ? ` (score: ${s.prob_score.toFixed(2)})` : "";
      probOut.textContent = s.probabilidade + scoreStr;
      if (next2) next2.disabled = false;
    } else {
      probOut.textContent = "—";
      if (next2) next2.disabled = true;
    }
  }

  // reidrata risco (Passo 4)
  renderRisco();

  // reidrata revisão (Passo 6)
  renderReview();

  // passo atual
  goto(s._step || 1);
})();
