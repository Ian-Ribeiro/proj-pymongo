const API = "http://localhost:8000";

const collectionSelect = document.getElementById("collectionSelect");
const btnLoad = document.getElementById("btnLoad");
const btnRefresh = document.getElementById("btnRefresh");
const docsList = document.getElementById("docsList");
const formContainer = document.getElementById("formContainer");
const btnInsert = document.getElementById("btnInsert");
const btnUpdate = document.getElementById("btnUpdate");
const btnReplace = document.getElementById("btnReplace");
const viewJson = document.getElementById("viewJson");
const resultArea = document.getElementById("resultArea");
const formTitle = document.getElementById("formTitle");

let currentTemplate = null;
let currentDocs = [];
let editingDocId = null;

async function fetchJson(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

async function loadCollections(){
  try{
    const cols = await fetchJson(`${API}/collections`);
    collectionSelect.innerHTML = cols.map(c => `<option value="${c}">${c}</option>`).join("");
  }catch(err){
    console.error(err);
    alert("Erro ao carregar coleções: " + err.message);
  }
}

async function loadCollectionData(){
  const col = collectionSelect.value;
  if (!col) return;
  try{
    currentDocs = await fetchJson(`${API}/documents/${encodeURIComponent(col)}`);
    currentTemplate = await fetchJson(`${API}/template/${encodeURIComponent(col)}`);
    renderDocs(currentDocs);
    buildFormFromTemplate(currentTemplate, null);
    editingDocId = null;
    btnUpdate.disabled = true;
    btnReplace.disabled = true;
    formTitle.textContent = `Inserir em '${col}'`;
    resultArea.textContent = "";
    viewJson.textContent = "";
  }catch(err){
    console.error(err);
    alert("Erro ao carregar dados: " + err.message);
  }
}

function renderDocs(docs){
  if (!docs || docs.length === 0){
    docsList.innerHTML = "<i>Nenhum documento.</i>";
    return;
  }
  docsList.innerHTML = "";
  docs.forEach(doc => {
    const item = document.createElement("div");
    item.className = "docItem";
    const meta = document.createElement("div");
    meta.className = "docMeta";
    meta.innerHTML = `<b>_id:</b> ${doc._id} <br> ${escapeHtml(JSON.stringify(doc, null, 2))}`;
    const actions = document.createElement("div");
    actions.className = "docActions";

    const btnView = document.createElement("button");
    btnView.textContent = "Ver";
    btnView.onclick = () => {
      viewJson.textContent = JSON.stringify(doc, null, 2);
    };

    const btnEdit = document.createElement("button");
    btnEdit.textContent = "Editar";
    btnEdit.onclick = () => {
      editingDocId = doc._id;
      populateFormWithDoc(doc);
      btnUpdate.disabled = false;
      btnReplace.disabled = false;
      formTitle.textContent = `Editando ${doc._id} (coleção: ${collectionSelect.value})`;
      window.scrollTo({top:0, behavior:"smooth"});
    };

    const btnDelete = document.createElement("button");
    btnDelete.textContent = "Deletar";
    btnDelete.onclick = async () => {
      if (!confirm("Confirmar exclusão?")) return;
      try{
        const result = await fetchJson(`${API}/delete/${encodeURIComponent(collectionSelect.value)}/${encodeURIComponent(doc._id)}`, {method:"DELETE"});
        resultArea.textContent = JSON.stringify(result, null, 2);
        await loadCollectionData();
      }catch(err){
        alert("Erro ao deletar: " + err.message);
      }
    };

    actions.appendChild(btnView);
    actions.appendChild(btnEdit);
    actions.appendChild(btnDelete);

    item.appendChild(meta);
    item.appendChild(actions);
    docsList.appendChild(item);
  });
}

function escapeHtml(s){
  return s.replace(/[&<>]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[ch]));
}

function buildFormFromTemplate(template, prefix){
  formContainer.innerHTML = ""; 
  const root = document.createElement("div");
  root.className = "formRoot";
  if (!template || Object.keys(template).length === 0) {
    root.innerHTML = "<i>Modelo vazio (coleção pode estar vazia).</i>";
    formContainer.appendChild(root);
    return;
  }
  _buildFields(template, root, prefix || "");
  formContainer.appendChild(root);
}

function _buildFields(obj, parentEl, namePrefix){
  for (const key of Object.keys(obj)){
    const sample = obj[key];
    const fieldName = namePrefix ? `${namePrefix}.${key}` : key;

    if (typeof sample === "object" && sample !== null && !Array.isArray(sample)){
      const fs = document.createElement("fieldset");
      const legend = document.createElement("legend");
      legend.textContent = key;
      fs.appendChild(legend);
      _buildFields(sample, fs, fieldName);
      parentEl.appendChild(fs);
    } else if (Array.isArray(sample)){
      const fs = document.createElement("fieldset");
      const legend = document.createElement("legend");
      legend.textContent = `${key} (Lista)`;
      fs.appendChild(legend);

      if (sample.length > 0 && typeof sample[0] === "object"){
        const listContainer = document.createElement("div");
        listContainer.className = "listContainer";
        listContainer.dataset.field = fieldName;
        const itemEl = document.createElement("div");
        itemEl.className = "listItem";
        itemEl.dataset.index = "0";
        _buildFields(sample[0], itemEl, `${fieldName}.0`);
        listContainer.appendChild(itemEl);

        const addBtn = document.createElement("button");
        addBtn.textContent = "Adicionar item";
        addBtn.type = "button";
        addBtn.onclick = () => {
          const idx = listContainer.querySelectorAll(".listItem").length;
          const newItem = document.createElement("div");
          newItem.className = "listItem";
          newItem.dataset.index = String(idx);
          _buildFields(sample[0], newItem, `${fieldName}.${idx}`);
          const rem = document.createElement("button");
          rem.type = "button";
          rem.textContent = "Remover";
          rem.onclick = () => { newItem.remove(); };
          newItem.appendChild(rem);
          listContainer.appendChild(newItem);
        };

        fs.appendChild(listContainer);
        fs.appendChild(addBtn);
      } else {
        const label = document.createElement("label");
        label.textContent = `${fieldName} (lista de valores)`;
        const ta = document.createElement("textarea");
        ta.name = fieldName;
        ta.rows = 3;
        ta.placeholder = "valor1, valor2, valor3";
        fs.appendChild(label);
        fs.appendChild(ta);
      }

      parentEl.appendChild(fs);
    } else {
      const label = document.createElement("label");
      label.textContent = fieldName;
      const input = document.createElement("input");
      input.name = fieldName;
      input.type = "text";
      input.placeholder = String(sample === null ? "" : sample);
      parentEl.appendChild(label);
      parentEl.appendChild(input);
    }
  }
}

function populateFormWithDoc(doc){
  buildFormFromTemplate(currentTemplate);
  const inputs = formContainer.querySelectorAll("input, textarea");
  inputs.forEach(inp => {
    const name = inp.name;
    const val = getValueByPath(doc, name);
    if (val === undefined || val === null) return;
    if (Array.isArray(val)){
      if (inp.tagName.toLowerCase() === "textarea"){
        inp.value = val.join(", ");
      } else {
        inp.value = JSON.stringify(val);
      }
    } else if (typeof val === "object"){
      inp.value = JSON.stringify(val);
    } else {
      inp.value = String(val);
    }
  });
}

function getValueByPath(obj, path){
  const parts = path.split(".");
  let ref = obj;
  for (let p of parts){
    if (ref === undefined) return undefined;
    if (/^\d+$/.test(p)){
      p = parseInt(p, 10);
    }
    ref = ref[p];
    if (ref === undefined) return undefined;
  }
  return ref;
}

function formToObject(){
  const data = {};
  const inputs = formContainer.querySelectorAll("input, textarea");
  inputs.forEach(inp => {
    const name = inp.name;
    if (!name) return;
    const raw = inp.value;
    if (inp.tagName.toLowerCase() === "textarea"){
      const arr = raw.split(",").map(s => s.trim()).filter(Boolean);
      setByPath(data, name, arr);
      return;
    }
    let value = raw;
    if (raw === "") {
      value = "";
    } else {
      try{
        const parsed = JSON.parse(raw);
        value = parsed;
      }catch(e){
        value = raw;
      }
    }
    setByPath(data, name, value);
  });
  return data;
}

function setByPath(obj, path, value){
  const parts = path.split(".");
  let ref = obj;
  for (let i = 0; i < parts.length; i++){
    let key = parts[i];
    const nextIsIndex = (i+1 < parts.length && /^\d+$/.test(parts[i+1]));
    if (/^\d+$/.test(key)){
      key = parseInt(key, 10);
    }
    if (i === parts.length - 1){
      if (typeof key === "number"){
        if (!Array.isArray(ref)) ref = []; 
        ref[key] = castValue(value);
      } else {
        ref[key] = castValue(value);
      }
      return;
    }
    const nextKey = parts[i+1];
    const nextIsNum = /^\d+$/.test(nextKey);

    if (typeof key === "number"){
      if (!Array.isArray(ref)) {
        ref = [];
      }
      if (!ref[key]) {
        ref[key] = nextIsNum ? [] : {};
      }
      ref = ref[key];
    } else {
      if (ref[key] === undefined) {
        ref[key] = nextIsNum ? [] : {};
      }
      ref = ref[key];
    }
  }
}

function castValue(v){
  if (typeof v === "string"){
    if (/^-?\d+(\.\d+)?$/.test(v)) return (v.indexOf('.')>-1 ? parseFloat(v) : parseInt(v,10));
    if (v.toLowerCase() === "true") return true;
    if (v.toLowerCase() === "false") return false;
  }
  return v;
}

btnLoad.onclick = loadCollectionData;
btnRefresh.onclick = loadCollectionData;

btnInsert.onclick = async () => {
  const col = collectionSelect.value;
  if (!col) return alert("Escolha a coleção.");
  const obj = formToObject();
  try {
    const res = await fetchJson(`${API}/insert/${encodeURIComponent(col)}`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(obj)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  } catch(err){
    alert("Erro inserindo: " + err.message);
  }
};

btnUpdate.onclick = async () => {
  if (!editingDocId) return alert("Escolha um documento para editar.");
  const col = collectionSelect.value;
  const patch = formToObject();
  try {
    const res = await fetchJson(`${API}/update/${encodeURIComponent(col)}/${encodeURIComponent(editingDocId)}`, {
      method: "PATCH",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(patch)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  } catch(err){
    alert("Erro ao atualizar: " + err.message);
  }
};

btnReplace.onclick = async () => {
  if (!editingDocId) return alert("Escolha um documento para substituir.");
  const col = collectionSelect.value;
  const newDoc = formToObject();
  try {
    const res = await fetchJson(`${API}/replace/${encodeURIComponent(col)}/${encodeURIComponent(editingDocId)}`, {
      method: "PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(newDoc)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  } catch(err){
    alert("Erro ao substituir: " + err.message);
  }
};

(async function init(){
  await loadCollections();
  if (collectionSelect.options.length > 0){
    collectionSelect.selectedIndex = 0;
    await loadCollectionData();
  }
})();
