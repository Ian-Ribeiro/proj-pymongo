const API = "http://127.0.0.1:8000";

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

// util: fetch json
async function fetchJson(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

// carrega coleções
async function loadCollections(){
  try{
    const cols = await fetchJson(`${API}/collections`);
    collectionSelect.innerHTML = cols.map(c => `<option value="${c}">${c}</option>`).join("");
  }catch(err){
    console.error(err);
    alert("Erro ao carregar coleções: " + err.message);
  }
}

// obtém lista de docs e template
async function loadCollectionData(){
  const col = collectionSelect.value;
  if (!col) return;
  try {
    currentDocs = await fetchJson(`${API}/documents/${encodeURIComponent(col)}`);

    if (currentDocs.length > 0) {
      // Usa o primeiro documento da coleção como base para o template do formulário
      currentTemplate = currentDocs[0];
    } else {
      currentTemplate = {}; // colecao vazia, form vazio
    }

    renderDocs(currentDocs);
    buildFormFromTemplate(currentTemplate, null);
    editingDocId = null;
    btnUpdate.disabled = true;
    btnReplace.disabled = true;
    formTitle.textContent = `Inserir em '${col}'`;
    resultArea.textContent = "";
    viewJson.textContent = "";
  } catch(err) {
    console.error(err);
    alert("Erro ao carregar dados: " + err.message);
  }
}


function escapeHtml(text) {
  return text.replace(/[&<>"]/g, function(ch) {
    switch (ch) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      default: return ch;
    }
  });
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

function buildFormFromTemplate(template, prefix){
  formContainer.innerHTML = ""; // limpa o container
  
  if (!template || Object.keys(template).length === 0) {
    const root = document.createElement("div");
    root.className = "formRoot";
    root.innerHTML = "<i>Modelo vazio (coleção pode estar vazia).</i>";
    formContainer.appendChild(root);
    return;
  }

  // Cria uma cópia do template para não modificar o original
  const filteredTemplate = {...template};
  // Remove o campo 'ativo' se existir
  if (filteredTemplate.hasOwnProperty("ativo")) {
    delete filteredTemplate.ativo;
  }

  const root = document.createElement("div");
  root.className = "formRoot";
  _buildFields(filteredTemplate, root, prefix || "");
  formContainer.appendChild(root);
}

// função interna que cria campos recursivamente
function _buildFields(obj, parentEl, namePrefix){
  for (const key of Object.keys(obj)){
    const sample = obj[key];
    const fieldName = namePrefix ? `${namePrefix}.${key}` : key;

    if (typeof sample === "object" && sample !== null && !Array.isArray(sample)){
      // subdocumento
      const fs = document.createElement("fieldset");
      const legend = document.createElement("legend");
      legend.textContent = key;
      fs.appendChild(legend);
      _buildFields(sample, fs, fieldName);
      parentEl.appendChild(fs);
    } else if (Array.isArray(sample)){
      // lista — se é lista de objetos, cria um bloco para itens com botão adicionar
      const fs = document.createElement("fieldset");
      const legend = document.createElement("legend");
      legend.textContent = `${key} (Lista)`;
      fs.appendChild(legend);

      if (sample.length > 0 && typeof sample[0] === "object"){
        // template item é sample[0]
        const listContainer = document.createElement("div");
        listContainer.className = "listContainer";
        listContainer.dataset.field = fieldName;
        // cria primeira item (index 0)
        const itemEl = document.createElement("div");
        itemEl.className = "listItem";
        itemEl.dataset.index = "0";
        _buildFields(sample[0], itemEl, `${fieldName}.0`);
        const rem = document.createElement("button");
        rem.type = "button";
        rem.textContent = "Remover";
        rem.onclick = () => { itemEl.remove(); };
        itemEl.appendChild(rem);

        listContainer.appendChild(itemEl);

        const addBtn = document.createElement("button");
        addBtn.textContent = "Adicionar item";
        addBtn.type = "button";
        addBtn.onclick = () => {
          const idx = listContainer.querySelectorAll(".listItem").length;
          const newItem = document.createElement("div");
          newItem.className = "listItem";
          newItem.dataset.index = idx.toString();
          _buildFields(sample[0], newItem, `${fieldName}.${idx}`);
          const rem2 = document.createElement("button");
          rem2.type = "button";
          rem2.textContent = "Remover";
          rem2.onclick = () => { newItem.remove(); };
          newItem.appendChild(rem2);
          listContainer.appendChild(newItem);
        };
        fs.appendChild(listContainer);
        fs.appendChild(addBtn);
      } else {
        // array simples: usar textarea, uma linha por valor
        const wrapper = document.createElement("div");
        wrapper.className = "formGroup";
        const label = document.createElement("label");
        label.textContent = `${key} (lista de valores)`;
        const ta = document.createElement("textarea");
        ta.name = fieldName;
        ta.rows = 3;
        ta.placeholder = "valor1, valor2, valor3";
        wrapper.appendChild(label);
        wrapper.appendChild(ta);
        fs.appendChild(wrapper);
      }
      parentEl.appendChild(fs);
    } else {
      // campo primitivo
      const wrapper = document.createElement("div");
      wrapper.className = "formGroup";
      const label = document.createElement("label");
      label.textContent = key;
      wrapper.appendChild(label);
      const input = document.createElement("input");
      input.name = fieldName;
      input.type = "text";
      input.placeholder = String(sample === null ? "" : sample);
      wrapper.appendChild(input);
      parentEl.appendChild(wrapper);
    }
  }
}

// Preenche o formulário com dados do documento (para edição)
function populateFormWithDoc(doc){
  // limpa tudo
  const inputs = formContainer.querySelectorAll("input,textarea");
  inputs.forEach(i => i.value = "");

  // preenche dados
  for(const [k,v] of Object.entries(doc)){
    setValueByPath(formContainer, k, v);
  }
}

function setValueByPath(container, path, value){
  // caminhos do tipo: campo.subcampo, ou campo.0.subcampo
  if (typeof value === "object" && value !== null){
    if (Array.isArray(value)){
      // array simples: coloca no textarea separado por vírgulas
      // array de objetos: deve montar dinamicamente a lista
      const listContainer = container.querySelector(`.listContainer[data-field="${path}"]`);
      if (listContainer){
        // remove itens atuais exceto o primeiro
        const items = listContainer.querySelectorAll(".listItem");
        items.forEach((item,i) => { if(i>0) item.remove(); });
        // preenche item 0
        if (value.length > 0 && typeof value[0] === "object"){
          populateFormWithDocList(listContainer.querySelector(".listItem"), value[0]);
          // adiciona os outros itens
          for(let i=1;i<value.length;i++){
            const addBtn = listContainer.nextElementSibling;
            addBtn.click();
            const newItem = listContainer.querySelector(`.listItem[data-index="${i}"]`);
            populateFormWithDocList(newItem, value[i]);
          }
        } else {
          // array simples
          const ta = container.querySelector(`textarea[name="${path}"]`);
          if(ta) ta.value = value.join(", ");
        }
      } else {
        // array simples fora de listContainer
        const ta = container.querySelector(`textarea[name="${path}"]`);
        if(ta) ta.value = value.join(", ");
      }
    } else {
      // objeto: atribuir recursivamente
      for(const [subk, subv] of Object.entries(value)){
        setValueByPath(container, `${path}.${subk}`, subv);
      }
    }
  } else {
    // primitivo: atribuir valor ao input/textarea
    const input = container.querySelector(`[name="${path}"]`);
    if(input){
      input.value = value;
    }
  }
}

function populateFormWithDocList(container, obj){
  for(const [k,v] of Object.entries(obj)){
    setValueByPath(container, k, v);
  }
}

// Coleta valores do formulário em objeto
function collectFormData(){
  const data = {};
  // inputs e textareas
  const inputs = formContainer.querySelectorAll("input,textarea");
  inputs.forEach(input => {
    const name = input.name;
    if (!name) return;
    const val = input.value.trim();
    if (val === "") return;

    // seta no objeto data com suporte a caminhos com '.'
    setObjectValue(data, name, val, input.tagName.toLowerCase());
  });

  return data;
}

// Função para atribuir valor em objeto pelo caminho com pontos, criando objetos aninhados conforme necessário
function setObjectValue(obj, path, val, tagName){
  const keys = path.split(".");
  let cur = obj;
  for(let i=0;i<keys.length-1;i++){
    const k = keys[i];
    if (!(k in cur)) cur[k] = {};
    cur = cur[k];
  }
  const lastKey = keys[keys.length-1];

  // Se é textarea e o valor é lista, parseia para array simples
  if(tagName === "textarea"){
    const arr = val.split(",").map(s=>s.trim()).filter(s=>s.length>0);
    cur[lastKey] = arr;
  } else {
    cur[lastKey] = val;
  }
}

// Envio do formulário
async function insertDoc(){
  const data = collectFormData();
  try{
    const col = collectionSelect.value;
    if (!col) {
      alert("Selecione uma coleção");
      return;
    }
    const res = await fetchJson(`${API}/insert/${encodeURIComponent(col)}`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  }catch(err){
    alert("Erro ao inserir: " + err.message);
  }
}

async function updateDoc(){
  if (!editingDocId){
    alert("Nenhum documento selecionado para atualizar.");
    return;
  }
  const data = collectFormData();
  try{
    const col = collectionSelect.value;
    const id = editingDocId;
    const res = await fetchJson(`${API}/update/${encodeURIComponent(col)}/${encodeURIComponent(id)}`, {
      method:"PUT",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  }catch(err){
    alert("Erro ao atualizar: " + err.message);
  }
}

async function replaceDoc(){
  if (!editingDocId){
    alert("Nenhum documento selecionado para substituir.");
    return;
  }
  const data = collectFormData();
  try{
    const col = collectionSelect.value;
    const id = editingDocId;
    const res = await fetchJson(`${API}/replace/${encodeURIComponent(col)}/${encodeURIComponent(id)}`, {
      method:"PUT",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });
    resultArea.textContent = JSON.stringify(res, null, 2);
    await loadCollectionData();
  }catch(err){
    alert("Erro ao substituir: " + err.message);
  }
}

btnLoad.onclick = loadCollectionData;
btnRefresh.onclick = loadCollections;
btnInsert.onclick = insertDoc;
btnUpdate.onclick = updateDoc;
btnReplace.onclick = replaceDoc;

window.onload = async () => {
  await loadCollections();
};
