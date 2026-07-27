<script setup>
import { ref } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  label: { type: String, default: "Image" },
  maxMb: { type: Number, default: 5 },
});
const emit = defineEmits(["update:modelValue"]);

const dragOver = ref(false);
const uploading = ref(false);
const error = ref("");
const inputEl = ref(null);

const ACCEPT = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"];

function browse() {
  inputEl.value?.click();
}

function onDrop(event) {
  dragOver.value = false;
  const file = event.dataTransfer?.files?.[0];
  if (file) upload(file);
}

function onPick(event) {
  const file = event.target.files?.[0];
  if (file) upload(file);
  event.target.value = "";
}

async function upload(file) {
  error.value = "";
  if (!ACCEPT.includes(file.type)) {
    error.value = "Please choose a PNG, JPG, WEBP or GIF image.";
    return;
  }
  if (file.size > props.maxMb * 1024 * 1024) {
    error.value = `Image must be under ${props.maxMb} MB.`;
    return;
  }
  uploading.value = true;
  try {
    const data = new FormData();
    data.append("file", file, file.name);
    data.append("is_private", "0");
    data.append("folder", "Home/Attachments");
    data.append("optimize", "1");
    const response = await fetch("/api/method/upload_file", {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-Frappe-CSRF-Token": window.csrf_token || "" },
      body: data,
    });
    const payload = await response.json().catch(() => ({}));
    if (response.status === 401 || payload.exc_type === "AuthenticationError") {
      window.dispatchEvent(new CustomEvent("retail-erp:session-expired"));
      throw new Error("Your session expired.");
    }
    if (!response.ok || payload.exc || !payload.message?.file_url) {
      let message = null;
      try { if (payload._server_messages) message = JSON.parse(JSON.parse(payload._server_messages)[0] || "{}").message; } catch { message = null; }
      throw new Error(message || "Upload failed.");
    }
    emit("update:modelValue", payload.message.file_url);
  } catch (caught) {
    error.value = caught.message || "Upload failed.";
  } finally {
    uploading.value = false;
  }
}

function clear() {
  emit("update:modelValue", "");
  error.value = "";
}
</script>

<template>
  <div class="img-upload">
    <span class="img-upload__label">{{ label }}</span>
    <div
      v-if="!modelValue"
      class="img-upload__drop"
      :class="{ 'is-over': dragOver, 'is-busy': uploading }"
      role="button"
      tabindex="0"
      @click="browse"
      @keydown.enter.prevent="browse"
      @keydown.space.prevent="browse"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <span v-if="uploading">Uploading…</span>
      <span v-else><strong>Drag &amp; drop</strong> an image here, or <u>browse</u></span>
      <small>PNG / JPG / WEBP / GIF, up to {{ maxMb }} MB</small>
    </div>
    <div v-else class="img-upload__preview">
      <img :src="modelValue" :alt="label" />
      <div class="img-upload__actions">
        <button type="button" class="img-upload__btn" @click="browse">Replace</button>
        <button type="button" class="img-upload__btn is-danger" @click="clear">Remove</button>
      </div>
    </div>
    <p v-if="error" class="img-upload__error" role="alert">{{ error }}</p>
    <input ref="inputEl" type="file" accept="image/*" class="img-upload__input" @change="onPick" />
  </div>
</template>

<style scoped>
.img-upload{display:grid;gap:.35rem}
.img-upload__label{font-weight:700}
.img-upload__drop{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.3rem;min-height:120px;padding:1rem;border:2px dashed var(--ref-border-colour);border-radius:.9rem;background:var(--ref-card-background);color:var(--ref-secondary-text);cursor:pointer;text-align:center}
.img-upload__drop.is-over{border-color:var(--ref-accent-orange,#e67e22);background:var(--ref-success-background)}
.img-upload__drop.is-busy{opacity:.7;cursor:progress}
.img-upload__drop small{font-size:.78rem}
.img-upload__drop:focus-visible{outline:3px solid var(--ref-accent-orange,#e67e22);outline-offset:2px}
.img-upload__preview{display:flex;gap:.6rem;align-items:center}
.img-upload__preview img{width:96px;height:96px;object-fit:cover;border-radius:.7rem;border:1px solid var(--ref-border-colour)}
.img-upload__actions{display:flex;flex-direction:column;gap:.4rem}
.img-upload__btn{min-height:36px;padding:0 .8rem;border:1px solid var(--ref-border-colour);border-radius:.55rem;background:var(--ref-card-background);color:var(--ref-primary-text);cursor:pointer;font-weight:600}
.img-upload__btn.is-danger{color:var(--ref-danger)}
.img-upload__error{color:var(--ref-danger);font-weight:600;margin:0}
.img-upload__input{display:none}
</style>
