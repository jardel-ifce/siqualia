// appcc_teste.js

const API_BASE = "http://localhost:8100"; // se servir front e API na mesma origem, deixe "".

const el = id => document.getElementById(id);

/* ------------------ META local (fallback) ------------------ */
const LOCAL_META = {
  umidade_mel: {type:"enum", label:"Umidade do mel", unit:"%", options:[
    {label:"≤ 18%", value:0},{label:"18–20%", value:1},{label:"> 20%", value:2}
  ], help:"Faixas usuais de umidade. Valores altos ↑ aumentam risco."},

  higienizacao_previa:{type:"enum", label:"Higienização prévia", options:[
    {label:"Ausente",value:0},{label:"Parcial",value:1},{label:"Adequada",value:2}
  ]},
  manipulador_higiene:{type:"enum", label:"Higiene do manipulador", options:[
    {label:"Ruim",value:0},{label:"Regular",value:1},{label:"Boa",value:2}
  ]},
  uso_epi:{type:"enum", label:"Uso de EPI", options:[
    {label:"Nenhum",value:0},{label:"Parcial",value:1},{label:"Completo",value:2}
  ]},
  local_envase:{type:"enum", label:"Condição do local", options:[
    {label:"Inadequado",value:0},{label:"Adequado",value:1}
  ]},
  temperatura_envase:{type:"range", label:"Temperatura no envase", min:18, max:60, step:1, unit:"°C"},
  tempo_exposicao_ar:{type:"range", label:"Exposição ao ar", min:0, max:60, step:1, unit:"min"},
  aspecto_visual:{type:"enum", label:"Aspecto visual", options:[
    {label:"Anômalo",value:0},{label:"Padrão",value:1},{label:"Excelente",value:2}
  ]},

  tipo_embalagem:{type:"enum", label:"Tipo de embalagem", options:[
    {label:"Vidro",value:0},{label:"PET grau alimentício",value:1},{label:"Outro aprovado",value:2}
  ]},
  estado_embalagem:{type:"enum", label:"Estado da embalagem", options:[
    {label:"Danificada",value:0},{label:"Íntegra",value:1}
  ]},
  tampa_correta:{type:"bool", label:"Tampa correta/apertada"},
  vedacao_adequada:{type:"bool", label:"Vedações adequadas"},
  cristalizacao:{type:"bool", label:"Cristalização presente"},

  rotulo_presente:{type:"bool", label:"Rótulo presente"},
  informacoes_completas:{type:"bool", label:"Informações completas no rótulo"},
  data_validade_legivel:{type:"bool", label:"Data de validade legível"},
  lote_identificado:{type:"bool", label:"Lote identificado"},
  registro_lote:{type:"bool", label:"Registro de lote"},
  treinamento_equipe:{type:"enum", label:"Treinamento da equipe", options:[
    {label:"Sem treinamento",value:0},{label:"Básico",value:1},{label:"Atualizado",value:2}
  ]},
  historico_reclamacoes:{type:"range", label:"Reclamações no período", min:0, max:50, step:1}
};

/* ------------------ helpers HTTP ------------------ */
async function getJSON(path){
  const r = await fetch(API_BASE + path);
  if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}
async function postJSON(path, body){
  const r = await fetch(API_BASE + path, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });
  const data = await r.json().catch(()=> ({}));
  if(!r.ok) {
    const msg = (data && data.detail) ? JSON.stringify(data.detail) : `${r.status} ${r.statusText}`;
    throw new Error(msg);
  }
  return data;
}

/* ------------------ status / UI ------------------ */
function setAPIStatus(ok, msg){
  el("apiStatus").textContent = ok ? `OK${msg? " • "+msg:""}` : `ERRO${msg? " • "+msg:""}`;
  el("apiStatus").style.color = ok ? "var(--ok)" : "var(--danger)";
}
async function pingAPI(){
  try {
    const cat = await getJSON("/api/models/catalog");
    const combos = cat?.best_by_combo ? Object.keys(cat.best_by_combo).length : 0;
    setAPIStatus(true, `${combos} combos`);
  } catch(e){
    setAPIStatus(false, String(e.message || e));
  }
}
function badgeClass(nome){
  const m = String(nome || "").toUpperCase();
  if(m.includes("ALTA")) return "risk-badge risk-alto";
  if(m.includes("MÉDIA") || m.includes("MEDIA")) return "risk-badge risk-medio";
  if(m.includes("BAIXA")) return "risk-badge risk-baixo";
  return "risk-badge risk-desp";
}

/* ------------------ esquema (API ou fallback) ------------------ */
let REMOTE_SCHEMA = null;
async function loadSchema(etapa, perigo){
  try{
    const resp = await getJSON(`/api/features/schema?etapa=${etapa}&perigo=${perigo}&only_model_features=true`);
    if(resp.ok && resp.schema){ REMOTE_SCHEMA = resp.schema; }
  }catch(e){ /* fallback LOCAL_META continua valendo */ }
}
function humanize(key){
  return key.replace(/_/g,' ')
            .replace(/\b([a-z])/g, m=>m.toUpperCase())
            .replace(/\bPct\b/,'(%)')
            .replace(/\bH\b/,'(h)')
            .replace(/\bC\b/,'(°C)');
}

function metaFor(feature){
  const m = (REMOTE_SCHEMA && REMOTE_SCHEMA[feature]) || LOCAL_META[feature] || {};
  if(!m.label){
    m.label = humanize(feature);         // título legível automático
  }
  return m;
}

async function fetchImportance(etapa, perigo, n /* pode ser undefined */){
  const url = (typeof n === "number")
    ? `/api/importance/top?etapa=${etapa}&perigo=${perigo}&n=${n}`
    : `/api/importance/top?etapa=${etapa}&perigo=${perigo}`;
  const imp = await getJSON(url);
  if(!imp.ok) throw new Error("Falha ao obter importance.");
  const order = Array.isArray(imp.order) ? imp.order : (imp.top||[]).map(r=>r.feature);
  const recommended = Number.isFinite(imp.recommended_n) ? imp.recommended_n : Math.min(8, order.length);
  const top = (imp.top||[]).map(r=>r.feature).slice(0, recommended);
  return { order, top, recommended };
}

/* ------------------ Top-N & Full features ------------------ */
async function fetchTopFeatures(etapa, perigo, n){
  try {
    const imp = await getJSON(`/api/importance/top?etapa=${etapa}&perigo=${perigo}&n=${n}`);
    if(imp.ok && Array.isArray(imp.top)){
      const names = imp.top.map(r => r.feature).filter(Boolean);
      if(names.length) return names;
    }
  } catch(e){ /* segue fallback */ }
  const st = await getJSON(`/api/models/status?etapa=${etapa}`);
  const info = st?.modelos?.[etapa]?.[perigo];
  if(info?.ok && Array.isArray(info.features_usadas)) {
    return info.features_usadas.slice(0, Math.max(1, n));
  }
  throw new Error("Não foi possível obter Top-N features.");
}
async function fetchFullFeatures(etapa, perigo){
  const st = await getJSON(`/api/models/status?etapa=${etapa}`);
  const info = st?.modelos?.[etapa]?.[perigo];
  if(info?.ok && Array.isArray(info.features_usadas)) return info.features_usadas;
  throw new Error("Sem features_usadas para esta combinação.");
}

/* ------------------ form builders ------------------ */
function buildInput(feature, meta, isTop){
  const id = `f_${feature}`;
  const label = meta?.label || feature;
  const unit = meta?.unit ? `<span class="unit">${meta.unit}</span>` : "";
  const badge = isTop ? `<span class="badge badge-top">TOP</span>` : "";
  const header = `
    <div class="field-header">
      <div class="field-title">${label}${unit}</div>
      ${badge}
    </div>
    <div class="field-meta">${feature}</div>
  `;
  const help = meta?.help ? `<div class="help">${meta.help}</div>` : "";
  const wrapOpen = `<div class="field${isTop ? "" : " is-other"}">`;
  const wrapClose = `</div>`;

  if(meta && meta.type === "enum" && Array.isArray(meta.options)){
    const opts = meta.options.map(o => `<option value="${o.value}">${o.label}</option>`).join("");
    return `${wrapOpen}${header}<select id="${id}">${opts}</select>${help}${wrapClose}`;
  }
  if(meta && meta.type === "bool"){
    return `${wrapOpen}${header}
      <div class="bool-row">
        <div class="switch" data-for="${id}"><input id="${id}" type="checkbox"/><div class="thumb"></div></div>
        <div class="switch-label">${label}</div>
      </div>
      <div class="bool-hints"><span>Não</span><span>Sim</span></div>
      ${help}${wrapClose}`;
  }
  if(meta && meta.type === "range"){
    const min = meta.min ?? 0, max = meta.max ?? 100, step = meta.step ?? 1;
    return `${wrapOpen}${header}
      <div class="inline">
        <input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${min}">
        <input id="${id}_num" type="number" step="${step}" value="${min}" style="max-width:110px"/>
      </div>${help}${wrapClose}`;
  }
  return `${wrapOpen}${header}<input id="${id}" type="number" step="any"/>${help}${wrapClose}`;
}

function buildForm(features, topSet = new Set()){
  const area = el("formArea");
  area.innerHTML = "";

  const tops = features.filter(f => topSet.has(f));
  const others = features.filter(f => !topSet.has(f));

  const wrap = document.createElement("div");
  wrap.className = "form-sections";

  const secTop = document.createElement("div");
  secTop.innerHTML = `<div class="section-title">Principais (Top-N)</div><div class="fields" id="secTop"></div>`;
  const secOut = document.createElement("div");
  secOut.innerHTML = `<div class="section-title">Outros</div><div class="fields" id="secOut"></div>`;

  wrap.appendChild(secTop);
  wrap.appendChild(secOut);
  area.appendChild(wrap);

  const secTopGrid = secTop.querySelector("#secTop");
  const secOutGrid = secOut.querySelector("#secOut");

  tops.forEach(f=>{
    const meta = metaFor(f);
    secTopGrid.insertAdjacentHTML("beforeend", buildInput(f, meta, true));
  });
  others.forEach(f=>{
    const meta = metaFor(f);
    secOutGrid.insertAdjacentHTML("beforeend", buildInput(f, meta, false));
  });

  // sync range <-> number
  features.forEach(f=>{
    const meta = metaFor(f);
    if(meta?.type === "range"){
      const id = `f_${f}`, numId = `f_${f}_num`;
      const rng = el(id), num = el(numId);
      if(rng && num){
        rng.addEventListener("input", ()=> { num.value = rng.value; });
        num.addEventListener("input", ()=> { rng.value = num.value; });
      }
    }
  });

  // switches visuais
  [...area.querySelectorAll(".switch")].forEach(sw=>{
    const input = el(sw.dataset.for);
    const set = () => sw.classList.toggle("checked", !!input.checked);
    sw.addEventListener("click", ()=> { input.checked = !input.checked; set(); });
    set();
  });
}

function autoFill(features){
  features.forEach((f,i)=>{
    const meta = metaFor(f);
    const id = `f_${f}`;
    if(meta?.type === "bool"){
      const ck = el(id); if(ck){ ck.checked = (i%3!==0); const sw = document.querySelector(`.switch[data-for="${id}"]`); if(sw) sw.classList.toggle("checked", ck.checked); }
      return;
    }
    if(meta?.type === "enum"){
      const sel = el(id);
      if(sel){ const len = sel.options.length; sel.selectedIndex = (i % len); }
      return;
    }
    if(meta?.type === "range"){
      const rng = el(id), num = el(`${id}_num`);
      if(rng && num){
        const min = Number(rng.min)||0, max = Number(rng.max)||100;
        const v = Math.round(min + ((i%5)/(5-1))*(max-min));
        rng.value = v; num.value = v;
      }
      return;
    }
    const inp = el(id); if(inp) inp.value = (i%5===0)?1:(i%5===1)?2:(i%5===2)?0:(i%5===3)?15:25;
  });
}

function readForm(features){
  const data = {};
  const missing = [];
  for(const f of features){
    const meta = metaFor(f);
    const id = `f_${f}`;
    if(meta?.type === "enum"){
      const sel = el(id);
      if(!sel) { missing.push(f); continue; }
      const val = Number(sel.value);
      if(Number.isNaN(val)) { missing.push(f); continue; }
      data[f] = val;
      continue;
    }
    if(meta?.type === "bool"){
      const ck = el(id);
      if(!ck) { missing.push(f); continue; }
      data[f] = ck.checked ? 1 : 0;
      continue;
    }
    if(meta?.type === "range"){
      const rng = el(id);
      if(!rng) { missing.push(f); continue; }
      const val = Number(rng.value);
      if(Number.isNaN(val)) { missing.push(f); continue; }
      data[f] = val;
      continue;
    }
    const inp = el(id);
    const val = Number(inp?.value ?? "");
    if(!inp || Number.isNaN(val)) { missing.push(f); continue; }
    data[f] = val;
  }
  return {data, missing};
}


/* ------------------ leitura & conversão ------------------ */
function readForm(features){
  const data = {};
  const missing = [];

  for(const f of features){
    const meta = metaFor(f);
    const id = `f_${f}`;
    if(meta?.type === "enum"){
      const sel = el(id);
      if(!sel) { missing.push(f); continue; }
      const val = Number(sel.value);
      if(Number.isNaN(val)) { missing.push(f); continue; }
      data[f] = val;
      continue;
    }
    if(meta?.type === "bool"){
      const ck = el(id);
      if(!ck) { missing.push(f); continue; }
      data[f] = ck.checked ? 1 : 0;
      continue;
    }
    if(meta?.type === "range"){
      const rng = el(id);
      if(!rng) { missing.push(f); continue; }
      const val = Number(rng.value);
      if(Number.isNaN(val)) { missing.push(f); continue; }
      data[f] = val;
      continue;
    }
    // default: numérico
    const inp = el(id);
    const val = Number(inp?.value ?? "");
    if(!inp || Number.isNaN(val)) { missing.push(f); continue; }
    data[f] = val;
  }
  return {data, missing};
}

/* ------------------ auto-preencher (demo) ------------------ */
function autoFill(features){
  features.forEach((f,i)=>{
    const meta = metaFor(f);
    const id = `f_${f}`;
    if(meta?.type === "bool"){
      const ck = el(id); if(ck) ck.checked = (i%3!==0);
      return;
    }
    if(meta?.type === "enum"){
      const sel = el(id);
      if(sel){
        const len = sel.options.length;
        sel.selectedIndex = (i % len);
      }
      return;
    }
    if(meta?.type === "range"){
      const rng = el(id), num = el(`${id}_num`);
      if(rng && num){
        const v = Math.round((Number(rng.min)||0) + ((i%5)/(5-1))*((Number(rng.max)||100)-(Number(rng.min)||0)));
        rng.value = v; num.value = v;
      }
      return;
    }
    const inp = el(id); if(inp) inp.value = (i%5===0)?1:(i%5===1)?2:(i%5===2)?0:(i%5===3)?15:25;
  });
}

/* ------------------ render resultado ------------------ */
function renderResult(resp){
  const resumo = el("outResumo");
  const box = el("outJSON");
  const cls = resp.prob_classe || resp.probabilidade || "—";
  resumo.className = badgeClass(cls);
  resumo.classList.remove("hidden");
  resumo.innerHTML = `
    <div><strong>Classe:</strong> ${cls} <span class="pill">score: ${("prob_score" in resp) ? resp.prob_score : "—"}</span></div>
    <div class="muted">etapa=${resp.etapa || "?"} • perigo=${resp.tipo_perigo || "?"} • modelo=${resp.modelo || "?"}</div>
  `;
  box.classList.remove("hidden");
  box.textContent = JSON.stringify(resp, null, 2);
}
function showError(err){
  const resumo = el("outResumo");
  const box = el("outJSON");
  resumo.className = "risk-badge risk-alto";
  resumo.classList.remove("hidden");
  resumo.innerHTML = `<strong>Erro</strong><div class="muted">${String(err.message || err)}</div>`;
  box.classList.remove("hidden");
  box.textContent = (err && err.stack) ? err.stack : String(err);
}

/* ------------------ handlers ------------------ */
async function onCarregar(){
  const etapa = el("etapa").value;
  const perigo = el("tipoPerigo").value;

  try{
    el("btnCarregar").disabled = true;

    // schema filtrado pelas features do modelo (nomes + labels)
    await loadSchema(etapa, perigo);

    // pega ordem, top e n recomendado
    const { order, top, recommended } = await fetchImportance(etapa, perigo);
    el("topN").value = recommended; // pré-carrega N sugerido

    // garante full features a partir do modelo
    const st = await getJSON(`/api/models/status?etapa=${etapa}`);
    const full = st?.modelos?.[etapa]?.[perigo]?.features_usadas || order;
    const topSet = new Set(top);
    const ordered = [...top, ...full.filter(f => !topSet.has(f))];

    buildForm(ordered, topSet);
    el("btnPredizer").disabled = false;
    setAPIStatus(true, `Top-N=${recommended} • ${ordered.length} campos`);
  }catch(e){
    buildForm([]);
    el("btnPredizer").disabled = true;
    showError(e);
    setAPIStatus(false, e.message || "erro");
  }finally{
    el("btnCarregar").disabled = false;
  }
}

async function onPredizer(){
  const etapa = el("etapa").value;
  const perigo = el("tipoPerigo").value;
  const st = await getJSON(`/api/models/status?etapa=${etapa}`);
  const full = st?.modelos?.[etapa]?.[perigo]?.features_usadas || [];
  if(full.length === 0){
    showError(new Error("Sem features_usadas para esta combinação."));
    return;
  }
  try{
    const rendered = [...document.querySelectorAll(".form-item input, .form-item select")]
      .map(inp => inp.id.replace(/^f_/, "").replace(/_num$/,""))
      .filter((v,i,arr)=> arr.indexOf(v)===i); // unique
    const features = rendered.length ? rendered : full;

    const parsed = readForm(features);
    if(parsed.missing.length){
      throw new Error("Campos ausentes/invalidos: " + parsed.missing.join(", "));
    }

    el("btnPredizer").disabled = true;
    const body = { etapa, tipo_perigo: perigo, bpfRespostas: parsed.data };
    const resp = await postJSON("/api/predicao", body);
    renderResult(resp);
    setAPIStatus(true, "predição OK");
  }catch(e){
    showError(e);
    setAPIStatus(false, e.message || "erro");
  }finally{
    el("btnPredizer").disabled = false;
  }
}

/* ------------------ bootstrap ------------------ */
window.addEventListener("DOMContentLoaded", ()=>{
  el("btnPing").onclick = pingAPI;
  el("btnCarregar").onclick = onCarregar;
  el("btnPredizer").onclick = onPredizer;
  el("btnLimpar").onclick = ()=>{
    el("formArea").innerHTML = "";
    el("outResumo").classList.add("hidden");
    el("outJSON").classList.add("hidden");
  };
  el("btnAutoFill").onclick = ()=>{
    const features = [...document.querySelectorAll(".form-item input, .form-item select")]
      .map(inp => inp.id.replace(/^f_/,"").replace(/_num$/,""))
      .filter((v,i,arr)=> arr.indexOf(v)===i);
    if(features.length===0){ return; }
    autoFill(features);
  };
  pingAPI();
});
